"""
AI Sales Agent Engine
Rule-based evaluation and insight generation for daily sales monitoring
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any


class SalesAgentEngine:
    """Core engine for evaluating sales performance and generating insights"""
    
    def __init__(self, data_path: str = 'data/daily_sales.csv'):
        self.data_path = data_path
        self.df = None
        self.latest_date = None
        
    def load_data(self) -> pd.DataFrame:
        """Load sales data from CSV"""
        try:
            self.df = pd.read_csv(self.data_path)
            self.df['date'] = pd.to_datetime(self.df['date'])
            self.latest_date = self.df['date'].max()
            return self.df
        except FileNotFoundError:
            print(f"⚠️ Data file not found: {self.data_path}")
            return None
    
    def get_latest_data(self) -> pd.DataFrame:
        """Get data for the most recent date"""
        if self.df is None:
            self.load_data()
        
        if self.df is not None and len(self.df) > 0:
            return self.df[self.df['date'] == self.latest_date].copy()
        return pd.DataFrame()
    
    def evaluate_rules(self, row: pd.Series) -> Dict[str, Any]:
        """
        Apply all rules to a single row and return status + violations
        
        Rules:
        R1: Target Achievement
        R2: Day-over-Day Performance
        R3: Trend Anomaly (vs 7-day average)
        R4: Weekend Adjustment
        """
        violations = []
        
        # R1: Target achievement
        delta_target = row.get('delta_vs_target', 0)
        if delta_target < -10:
            violations.append({
                'rule': 'R1.3',
                'severity': 'CRITICAL',
                'message': f"Missed target by {abs(delta_target):.1f}%"
            })
        elif delta_target < 0:
            violations.append({
                'rule': 'R1.2',
                'severity': 'WARNING',
                'message': f"Below target by {abs(delta_target):.1f}%"
            })
        
        # R2: Day-over-day performance
        delta_yesterday = row.get('delta_vs_yesterday', 0)
        if delta_yesterday < -15:
            violations.append({
                'rule': 'R2.3',
                'severity': 'CRITICAL',
                'message': f"Dropped {abs(delta_yesterday):.1f}% vs yesterday"
            })
        elif delta_yesterday < -5:
            violations.append({
                'rule': 'R2.2',
                'severity': 'WARNING',
                'message': f"Down {abs(delta_yesterday):.1f}% vs yesterday"
            })
        
        # R3: Trend anomaly (vs 7-day average)
        total_sales = row.get('total_sales', 0)
        avg_7d = row.get('avg_7d_sales', total_sales)
        
        if avg_7d > 0:
            trend_ratio = total_sales / avg_7d
            if trend_ratio < 0.70:
                violations.append({
                    'rule': 'R3.3',
                    'severity': 'CRITICAL',
                    'message': f"Sales {(1-trend_ratio)*100:.1f}% below 7-day average"
                })
            elif trend_ratio < 0.85:
                violations.append({
                    'rule': 'R3.2',
                    'severity': 'WARNING',
                    'message': f"Sales {(1-trend_ratio)*100:.1f}% below 7-day average"
                })
        
        # Determine final status
        if any(v['severity'] == 'CRITICAL' for v in violations):
            final_status = 'CRITICAL'
        elif any(v['severity'] == 'WARNING' for v in violations):
            final_status = 'WARNING'
        else:
            final_status = 'OK'
        
        # R4: Weekend adjustment
        adjustment_note = None
        is_weekend = row.get('is_weekend', False)
        if is_weekend and final_status == 'CRITICAL':
            final_status = 'WARNING'
            adjustment_note = 'Downgraded from CRITICAL due to weekend'
        
        return {
            'status': final_status,
            'violations': violations,
            'adjustment_note': adjustment_note
        }
    
    def process_daily_data(self) -> pd.DataFrame:
        """Process all rows and apply rule evaluation"""
        df_latest = self.get_latest_data()
        
        if df_latest.empty:
            return pd.DataFrame()
        
        results = []
        
        for idx, row in df_latest.iterrows():
            evaluation = self.evaluate_rules(row)
            
            result = {
                'date': row.get('date'),
                'region': row.get('region', row.get('city', 'Unknown')),
                'product': row.get('product', row.get('product_line', 'Unknown')),
                'total_sales': row.get('total_sales', row.get('sales', 0)),
                'target_daily': row.get('target_daily', 0),
                'delta_vs_target': row.get('delta_vs_target', 0),
                'delta_vs_yesterday': row.get('delta_vs_yesterday', 0),
                'day_name': row.get('day_name', ''),
                'is_weekend': row.get('is_weekend', False),
                'status': evaluation['status'],
                'violations': evaluation['violations'],
                'adjustment_note': evaluation['adjustment_note']
            }
            results.append(result)
        
        return pd.DataFrame(results)
    
    def aggregate_findings(self, df_results: pd.DataFrame) -> Dict[str, Any]:
        """Summarize results for dashboard and LLM consumption"""
        
        if df_results.empty:
            return self._empty_summary()
        
        summary = {
            'date': df_results['date'].iloc[0].strftime('%Y-%m-%d') if len(df_results) > 0 else '',
            'day_name': df_results['day_name'].iloc[0] if len(df_results) > 0 else '',
            'is_weekend': bool(df_results['is_weekend'].iloc[0]) if len(df_results) > 0 else False,
            'total_rows': len(df_results),
            'critical_count': len(df_results[df_results['status'] == 'CRITICAL']),
            'warning_count': len(df_results[df_results['status'] == 'WARNING']),
            'ok_count': len(df_results[df_results['status'] == 'OK']),
            'total_sales': float(df_results['total_sales'].sum()),
            'total_target': float(df_results['target_daily'].sum()),
        }
        
        # Calculate portfolio achievement
        if summary['total_target'] > 0:
            summary['portfolio_achievement'] = (summary['total_sales'] / summary['total_target']) * 100
        else:
            summary['portfolio_achievement'] = 0
        
        # Calculate delta vs yesterday (portfolio level)
        if 'delta_vs_yesterday' in df_results.columns:
            summary['delta_vs_yesterday'] = float(df_results['delta_vs_yesterday'].mean())
        else:
            summary['delta_vs_yesterday'] = 0
        
        # Determine overall status
        if summary['critical_count'] > 0:
            summary['overall_status'] = 'CRITICAL'
        elif summary['warning_count'] > 0:
            summary['overall_status'] = 'WARNING'
        else:
            summary['overall_status'] = 'OK'
        
        # Extract critical issues (top 5 by severity)
        critical_issues = df_results[df_results['status'] == 'CRITICAL'] \
            .sort_values('delta_vs_target') \
            .head(5)
        
        summary['critical_issues'] = critical_issues.to_dict('records') if not critical_issues.empty else []
        
        # Extract warnings (top 5)
        warning_issues = df_results[df_results['status'] == 'WARNING'] \
            .sort_values('delta_vs_target') \
            .head(5)
        
        summary['warning_issues'] = warning_issues.to_dict('records') if not warning_issues.empty else []
        
        # Identify top performers (for balanced reporting)
        top_performers = df_results[df_results['status'] == 'OK'] \
            .sort_values('delta_vs_target', ascending=False) \
            .head(3)
        
        summary['top_performers'] = top_performers.to_dict('records') if not top_performers.empty else []
        
        # Get all flagged items (CRITICAL + WARNING)
        flagged = df_results[df_results['status'].isin(['CRITICAL', 'WARNING'])].copy()
        summary['flagged_items'] = flagged.to_dict('records') if not flagged.empty else []
        
        return summary
    
    def _empty_summary(self) -> Dict[str, Any]:
        """Return empty summary structure"""
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'day_name': datetime.now().strftime('%A'),
            'is_weekend': False,
            'total_rows': 0,
            'critical_count': 0,
            'warning_count': 0,
            'ok_count': 0,
            'total_sales': 0,
            'total_target': 0,
            'portfolio_achievement': 0,
            'delta_vs_yesterday': 0,
            'overall_status': 'OK',
            'critical_issues': [],
            'warning_issues': [],
            'top_performers': [],
            'flagged_items': []
        }
    
    def generate_ai_insight(self, summary: Dict[str, Any]) -> str:
        """
        Generate AI-powered daily sales insight
        For POC: Uses template-based generation (no API key required)
        Can be replaced with real LLM API call
        
        INI ADALAH BAGIAN AI - Menghasilkan laporan penjualan dalam bahasa natural
        """
        
        status = summary['overall_status']
        date_str = summary['date']
        day_name = summary['day_name']
        
        # Translate day names to Indonesian
        day_translation = {
            'Monday': 'Senin',
            'Tuesday': 'Selasa',
            'Wednesday': 'Rabu',
            'Thursday': 'Kamis',
            'Friday': 'Jumat',
            'Saturday': 'Sabtu',
            'Sunday': 'Minggu'
        }
        day_name_id = day_translation.get(day_name, day_name)
        
        # Format currency
        total_sales = summary['total_sales']
        total_target = summary['total_target']
        achievement = summary['portfolio_achievement']
        delta_yesterday = summary['delta_vs_yesterday']
        
        # Build insight based on status
        insight = f"""🧾 LAPORAN PENJUALAN HARIAN — {day_name_id}, {date_str}

📌 **Ringkasan Eksekutif**
"""
        
        if status == 'CRITICAL':
            insight += f"""- Portofolio berkinerja jauh di bawah target: **{achievement:.1f}% dari target tercapai**
- {summary['critical_count']} masalah kritis memerlukan perhatian segera
- Penjualan {'menurun' if delta_yesterday < 0 else 'meningkat'} {abs(delta_yesterday):.1f}% vs kemarin
- Intervensi mendesak diperlukan untuk mencegah penurunan lebih lanjut
- Manajer regional harus menyelidiki akar masalah hari ini
"""
        elif status == 'WARNING':
            insight += f"""- Portofolio mencapai **{achievement:.1f}% dari target** — di bawah ekspektasi
- {summary['warning_count']} sinyal peringatan terdeteksi, {summary['critical_count']} masalah kritis
- Penjualan {'menurun' if delta_yesterday < 0 else 'meningkat'} {abs(delta_yesterday):.1f}% vs kemarin
- Pemantauan ketat diperlukan; siapkan rencana kontingensi
- Beberapa titik terang teridentifikasi pada performa terbaik
"""
        else:
            insight += f"""- Portofolio berkinerja baik: **{achievement:.1f}% dari target tercapai**
- Semua wilayah dan produk dalam rentang yang dapat diterima
- Penjualan {'menurun' if delta_yesterday < 0 else 'meningkat'} {abs(delta_yesterday):.1f}% vs kemarin
- Tidak ada kekhawatiran mendesak; pertahankan momentum saat ini
- Lanjutkan pemantauan untuk tren yang muncul
"""
        
        insight += f"""
📊 **Metrik Utama**
- **Total Penjualan**: Rp {total_sales:,.0f}
- **Target**: Rp {total_target:,.0f}
- **Selisih vs Target**: {achievement - 100:+.1f}%
- **Perubahan vs Kemarin**: {delta_yesterday:+.1f}%
"""
        
        # Add alerts section
        insight += "\n⚠️ **Peringatan & Risiko**\n"
        
        if summary['critical_issues']:
            for issue in summary['critical_issues'][:3]:  # Top 3
                region = issue.get('region', 'Unknown')
                product = issue.get('product', 'Unknown')
                sales = issue.get('total_sales', 0)
                delta_target = issue.get('delta_vs_target', 0)
                delta_yesterday = issue.get('delta_vs_yesterday', 0)
                
                insight += f"- 🚨 **KRITIS**: {region} - {product}: Rp {sales:,.0f} ({delta_target:+.1f}% vs target, {delta_yesterday:+.1f}% vs kemarin)\n"
        
        if summary['warning_issues']:
            for issue in summary['warning_issues'][:2]:  # Top 2
                region = issue.get('region', 'Unknown')
                product = issue.get('product', 'Unknown')
                delta_target = issue.get('delta_vs_target', 0)
                
                insight += f"- ⚠️ **PERINGATAN**: {region} - {product} ({delta_target:+.1f}% vs target)\n"
        
        if not summary['critical_issues'] and not summary['warning_issues']:
            insight += "- ✅ Tidak ada masalah kritis atau peringatan terdeteksi\n"
        
        # Add AI analysis
        insight += "\n🧠 **Analisis AI (Mengapa ini terjadi)**\n"
        
        if status == 'CRITICAL':
            insight += "- Penurunan tajam menunjukkan masalah operasional (inventori, staf, sistem) atau faktor eksternal (aktivitas kompetitor, cuaca)\n"
            insight += "- Beberapa masalah kritis mengindikasikan masalah sistemik yang memerlukan perhatian pimpinan\n"
            insight += "- Analisis pola menunjukkan ini bukan fluktuasi normal\n"
        elif status == 'WARNING':
            insight += "- Penurunan kinerja mungkin sementara, tetapi tren memerlukan pemantauan\n"
            insight += "- Beberapa wilayah/produk berkinerja buruk sementara yang lain mengkompensasi\n"
            insight += "- Pola akhir pekan/hari kerja mungkin mempengaruhi hasil\n"
        else:
            insight += "- Eksekusi kuat di semua wilayah dan lini produk\n"
            insight += "- Momentum penjualan positif dan berkelanjutan\n"
            insight += "- Strategi saat ini efektif\n"
        
        # Add recommendations
        insight += "\n🎯 **Tindakan yang Direkomendasikan (Hari Ini)**\n"
        
        if status == 'CRITICAL':
            insight += "1. **MENDESAK**: Manajer regional hubungi lokasi yang berkinerja buruk segera\n"
            insight += "2. **MENDESAK**: Verifikasi inventori, staf, dan fungsi sistem\n"
            insight += "3. Eskalasi ke VP Penjualan jika masalah tidak terselesaikan pada akhir hari\n"
            insight += "4. Siapkan rencana tindakan korektif untuk besok\n"
            insight += "5. Periksa ulang penjualan jam 3 sore untuk menilai efektivitas intervensi\n"
        elif status == 'WARNING':
            insight += "1. Tinjau kombinasi wilayah-produk yang ditandai untuk masalah yang diketahui\n"
            insight += "2. Periksa promosi kompetitor atau perubahan pasar\n"
            insight += "3. Siapkan kontingensi jika tren berlanjut besok\n"
            insight += "4. Pantau dengan ketat sepanjang hari\n"
            insight += "5. Dokumentasikan temuan untuk analisis pola\n"
        else:
            insight += "1. Lanjutkan strategi dan eksekusi penjualan saat ini\n"
            insight += "2. Bagikan praktik terbaik dari performa terbaik\n"
            insight += "3. Pertahankan tingkat inventori dan staf\n"
            insight += "4. Pantau untuk masalah yang muncul\n"
            insight += "5. Persiapkan untuk periode promosi mendatang\n"
        
        insight += f"\n**Status**: {'🚨' if status == 'CRITICAL' else '⚠️' if status == 'WARNING' else '✅'} {status}\n"
        
        return insight
    
    def run_analysis(self) -> Dict[str, Any]:
        """
        Main method to run complete analysis
        Returns summary with AI insight
        """
        # Process data
        df_results = self.process_daily_data()
        
        # Aggregate findings
        summary = self.aggregate_findings(df_results)
        
        # Generate AI insight
        summary['ai_insight'] = self.generate_ai_insight(summary)
        
        return summary


# Convenience function for quick testing
def analyze_sales(data_path: str = 'data/daily_sales.csv') -> Dict[str, Any]:
    """Quick analysis function"""
    engine = SalesAgentEngine(data_path)
    return engine.run_analysis()


if __name__ == '__main__':
    # Test the engine
    print("🤖 Testing Sales Agent Engine...\n")
    
    result = analyze_sales()
    
    print(f"Date: {result['date']}")
    print(f"Status: {result['overall_status']}")
    print(f"Total Sales: Rp {result['total_sales']:,.0f}")
    print(f"Achievement: {result['portfolio_achievement']:.1f}%")
    print(f"\nCritical: {result['critical_count']} | Warning: {result['warning_count']} | OK: {result['ok_count']}")
    print("\n" + "="*60)
    print(result['ai_insight'])
