import io
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import base64
from datetime import datetime

class AnalysisReport:
    """数据分析报告生成器"""
    
    def __init__(self):
        self.analysis_results = {}
        self.charts = {}
        self.summary_stats = {}
        
    def add_analysis_result(self, dimension_name, result_data, charts=None):
        """
        添加分析结果
        :param dimension_name: 分析维度名称
        :param result_data: 分析结果数据
        :param charts: 相关图表
        """
        self.analysis_results[dimension_name] = result_data
        if charts:
            self.charts[dimension_name] = charts
    
    def add_summary_stats(self, stats):
        """添加汇总统计信息"""
        self.summary_stats.update(stats)
    
    def generate_pdf_report(self, analysis_info):
        """
        生成完整的PDF报告
        :param analysis_info: 分析基本信息
        :return: PDF字节数据
        """
        try:
            # 创建PDF缓冲区
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # 获取样式
            styles = getSampleStyleSheet()
            story = []
            
            # 生成报告内容
            story.extend(self._generate_cover_page(analysis_info, styles))
            story.extend(self._generate_summary_section(styles))
            story.extend(self._generate_analysis_sections(styles))
            story.extend(self._generate_conclusion_section(styles))
            
            # 构建PDF
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            print(f"PDF生成错误: {str(e)}")
            return None
    
    def _generate_cover_page(self, analysis_info, styles):
        """生成封面页"""
        story = []
        
        # 标题样式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # 居中
            textColor=colors.HexColor('#2E4057')
        )
        
        # 副标题样式
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=16,
            spaceAfter=20,
            alignment=1,
            textColor=colors.HexColor('#5A6F7F')
        )
        
        # 信息样式
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            leftIndent=50,
            textColor=colors.HexColor('#333333')
        )
        
        # 报告标题
        story.append(Spacer(1, 50))
        story.append(Paragraph("📊 数据分析报告", title_style))
        story.append(Paragraph("Data Analysis Report", subtitle_style))
        story.append(Spacer(1, 50))
        
        # 分析信息
        story.append(Paragraph("<b>📋 分析信息 Analysis Information</b>", styles['Heading2']))
        story.append(Spacer(1, 20))
        
        info_data = [
            ["分析类型", analysis_info.get('analysis_name', 'N/A')],
            ["数据源", analysis_info.get('selected_sheet', 'N/A')],
            ["分析维度", ', '.join(analysis_info.get('selected_dimensions', []))],
            ["报告生成时间", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["数据行数", str(analysis_info.get('data_rows', 'N/A'))],
            ["数据列数", str(analysis_info.get('data_cols', 'N/A'))]
        ]
        
        info_table = Table(info_data, colWidths=[4*cm, 8*cm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9FA')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E0E0E0')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 30))
        
        # 页面分隔
        story.append(self._page_break())
        
        return story
    
    def _generate_summary_section(self, styles):
        """生成汇总统计部分"""
        story = []
        
        story.append(Paragraph("📈 执行摘要 Executive Summary", styles['Heading1']))
        story.append(Spacer(1, 20))
        
        # 如果有汇总统计数据
        if self.summary_stats:
            story.append(Paragraph("📊 关键指标 Key Metrics", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            # 创建指标表格
            metrics_data = []
            for key, value in self.summary_stats.items():
                metrics_data.append([key, str(value)])
            
            if metrics_data:
                metrics_table = Table(metrics_data, colWidths=[6*cm, 6*cm])
                metrics_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F1F8E9')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E0E0E0')),
                ]))
                story.append(metrics_table)
        else:
            story.append(Paragraph("✨ 分析已完成，详细结果请查看各分析模块。", styles['Normal']))
        
        story.append(Spacer(1, 20))
        story.append(self._page_break())
        
        return story
    
    def _generate_analysis_sections(self, styles):
        """生成各分析模块部分"""
        story = []
        
        story.append(Paragraph("🔍 详细分析结果 Detailed Analysis Results", styles['Heading1']))
        story.append(Spacer(1, 20))
        
        # 为每个分析维度生成单独的部分
        for i, (dimension_name, result_data) in enumerate(self.analysis_results.items(), 1):
            # 分析标题
            story.append(Paragraph(f"{i}. {dimension_name}", styles['Heading2']))
            story.append(Spacer(1, 15))
            
            # 分析描述
            if isinstance(result_data, dict):
                if 'description' in result_data:
                    story.append(Paragraph(f"📝 {result_data['description']}", styles['Normal']))
                    story.append(Spacer(1, 10))
                
                # 主要发现
                if 'findings' in result_data:
                    story.append(Paragraph("🔍 主要发现:", styles['Heading3']))
                    for finding in result_data['findings']:
                        story.append(Paragraph(f"• {finding}", styles['Normal']))
                    story.append(Spacer(1, 10))
                
                # 数据表格
                if 'data_table' in result_data and isinstance(result_data['data_table'], pd.DataFrame):
                    story.append(Paragraph("📊 数据详情:", styles['Heading3']))
                    story.append(Spacer(1, 5))
                    
                    # 转换DataFrame为表格
                    df = result_data['data_table'].head(10)  # 只显示前10行
                    table_data = [df.columns.tolist()] + df.values.tolist()
                    
                    if len(table_data) > 1:
                        data_table = Table(table_data)
                        data_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E3F2FD')),
                            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDBDBD')),
                        ]))
                        story.append(data_table)
                        story.append(Spacer(1, 10))
                
                # 统计信息
                if 'stats' in result_data:
                    story.append(Paragraph("📈 统计摘要:", styles['Heading3']))
                    for stat_key, stat_value in result_data['stats'].items():
                        story.append(Paragraph(f"• {stat_key}: {stat_value}", styles['Normal']))
                    story.append(Spacer(1, 10))
            
            else:
                # 简单文本结果
                story.append(Paragraph(f"📋 分析结果: {str(result_data)}", styles['Normal']))
            
            # 图表占位符（实际项目中可以嵌入图表图片）
            if dimension_name in self.charts:
                story.append(Paragraph("📊 相关图表:", styles['Heading3']))
                story.append(Paragraph("📈 图表将在系统中显示，PDF版本暂不包含交互图表。", styles['Normal']))
                story.append(Spacer(1, 10))
            
            story.append(Spacer(1, 20))
            
            # 每3个分析后分页
            if i % 3 == 0 and i < len(self.analysis_results):
                story.append(self._page_break())
        
        return story
    
    def _generate_conclusion_section(self, styles):
        """生成结论部分"""
        story = []
        
        story.append(self._page_break())
        story.append(Paragraph("💡 分析结论与建议 Conclusions & Recommendations", styles['Heading1']))
        story.append(Spacer(1, 20))
        
        # 总体结论
        story.append(Paragraph("🎯 总体结论:", styles['Heading2']))
        story.append(Paragraph("• 数据分析已顺利完成，各项指标已生成。", styles['Normal']))
        story.append(Paragraph("• 系统检测到的异常数据已被标记和处理。", styles['Normal']))
        story.append(Paragraph("• 建议定期进行数据质量检查和分析更新。", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # 改进建议
        story.append(Paragraph("🚀 改进建议:", styles['Heading2']))
        story.append(Paragraph("• 建立数据质量监控机制", styles['Normal']))
        story.append(Paragraph("• 优化数据收集流程", styles['Normal']))
        story.append(Paragraph("• 定期更新分析模型", styles['Normal']))
        story.append(Spacer(1, 30))
        
        # 报告结束
        end_style = ParagraphStyle(
            'EndStyle',
            parent=styles['Normal'],
            fontSize=10,
            alignment=1,
            textColor=colors.HexColor('#666666')
        )
        story.append(Paragraph("--- 报告结束 End of Report ---", end_style))
        
        return story
    
    def _page_break(self):
        """创建分页符"""
        from reportlab.platypus import PageBreak
        return PageBreak()

def generate_sample_report_data():
    """生成示例报告数据"""
    report = AnalysisReport()
    
    # 添加示例分析结果
    report.add_analysis_result("异常数据清洗", {
        "description": "对数据进行全面的异常值检测和清洗处理",
        "findings": [
            "检测到15条异常数据记录",
            "主要异常类型为数值超出合理范围",
            "异常数据已按用户配置进行处理"
        ],
        "stats": {
            "异常数据数量": 15,
            "清洗后数据量": 1285,
            "数据质量得分": "92%"
        }
    })
    
    report.add_analysis_result("ABC分析", {
        "description": "按照帕累托法则对物品进行重要性分类",
        "findings": [
            "A类物品占总数的20%，贡献80%的价值",
            "B类物品需要优化管理策略",
            "C类物品可以简化管理流程"
        ],
        "stats": {
            "A类物品数量": 156,
            "B类物品数量": 312,
            "C类物品数量": 832
        }
    })
    
    # 添加汇总统计
    report.add_summary_stats({
        "总分析维度": 2,
        "数据处理完成度": "100%",
        "报告生成时间": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    
    return report 