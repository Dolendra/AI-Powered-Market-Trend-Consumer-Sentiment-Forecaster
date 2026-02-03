"""
Interactive Plotly dashboard for sentiment analysis visualization.
Creates comprehensive visualizations with Plotly.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROCESSED_DATA_DIR
from analytics import SentimentAnalyzer

logger = logging.getLogger(__name__)


class SentimentDashboard:
    """Interactive Plotly dashboard for sentiment analysis."""
    
    def __init__(self, data_file: Path = None):
        """
        Initialize dashboard with data.
        
        Args:
            data_file: Path to feature_sentiment_cleaned.csv
        """
        if data_file is None:
            data_file = PROCESSED_DATA_DIR / "feature_sentiment_cleaned.csv"
        
        self.data_file = data_file
        self.df = None
        self.analyzer = None
        self.load_data()
    
    def load_data(self) -> None:
        """Load and prepare data."""
        try:
            self.df = pd.read_csv(self.data_file)
            self.analyzer = SentimentAnalyzer(self.data_file)
            logger.info(f"[OK] Loaded {len(self.df)} records for dashboard")
        except FileNotFoundError:
            logger.error(f"[ERROR] Data file not found: {self.data_file}")
            raise
    
    def create_sentiment_distribution_chart(self) -> go.Figure:
        """Create sentiment distribution pie chart."""
        sentiment_counts = self.df["sentiment"].value_counts()
        
        colors = {
            "positive": "#2ecc71",
            "negative": "#e74c3c",
            "neutral": "#95a5a6"
        }
        
        fig = go.Figure(data=[go.Pie(
            labels=sentiment_counts.index,
            values=sentiment_counts.values,
            hole=0.4,
            marker=dict(colors=[colors.get(s, "#95a5a6") for s in sentiment_counts.index]),
            textinfo="label+percent",
            textposition="outside"
        )])
        
        fig.update_layout(
            title={
                "text": "Overall Sentiment Distribution",
                "x": 0.5,
                "xanchor": "center"
            },
            font=dict(size=14),
            showlegend=True,
            height=500
        )
        
        return fig
    
    def create_feature_sentiment_heatmap(self) -> go.Figure:
        """Create heatmap of sentiment by feature."""
        # Create pivot table
        pivot = pd.crosstab(
            self.df["feature"],
            self.df["sentiment"],
            normalize="index"
        ) * 100
        
        # Reorder columns
        pivot = pivot[["positive", "neutral", "negative"]]
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale=[[0, "#e74c3c"], [0.5, "#95a5a6"], [1, "#2ecc71"]],
            text=pivot.values.round(1),
            texttemplate="%{text}%",
            textfont={"size": 10},
            colorbar=dict(title="Percentage")
        ))
        
        fig.update_layout(
            title={
                "text": "Sentiment Distribution by Feature (%)",
                "x": 0.5,
                "xanchor": "center"
            },
            xaxis_title="Sentiment",
            yaxis_title="Feature",
            height=600,
            font=dict(size=12)
        )
        
        return fig
    
    def create_feature_sentiment_scores(self) -> go.Figure:
        """Create bar chart of sentiment scores by feature."""
        feature_sentiments = self.analyzer.get_feature_sentiments()
        
        features = list(feature_sentiments.keys())
        scores = [feature_sentiments[f]["sentiment_score"] for f in features]
        
        # Sort by score
        sorted_data = sorted(zip(features, scores), key=lambda x: x[1], reverse=True)
        features, scores = zip(*sorted_data)
        
        colors = ["#2ecc71" if s > 0 else "#e74c3c" if s < 0 else "#95a5a6" for s in scores]
        
        fig = go.Figure(data=[go.Bar(
            x=list(features),
            y=list(scores),
            marker_color=colors,
            text=[f"{s:.2f}" for s in scores],
            textposition="outside"
        )])
        
        fig.update_layout(
            title={
                "text": "Sentiment Score by Feature",
                "x": 0.5,
                "xanchor": "center"
            },
            xaxis_title="Feature",
            yaxis_title="Sentiment Score (-1 to +1)",
            xaxis={"tickangle": -45},
            height=500,
            yaxis=dict(range=[-1, 1])
        )
        
        return fig
    
    def create_model_comparison(self) -> go.Figure:
        """Create comparison chart across product models."""
        model_sentiments = self.analyzer.get_model_sentiments()
        
        models = list(model_sentiments.keys())
        positive = [model_sentiments[m]["positive"] for m in models]
        negative = [model_sentiments[m]["negative"] for m in models]
        neutral = [model_sentiments[m]["neutral"] for m in models]
        
        fig = go.Figure(data=[
            go.Bar(name="Positive", x=models, y=positive, marker_color="#2ecc71"),
            go.Bar(name="Neutral", x=models, y=neutral, marker_color="#95a5a6"),
            go.Bar(name="Negative", x=models, y=negative, marker_color="#e74c3c")
        ])
        
        fig.update_layout(
            title={
                "text": "Sentiment Distribution by Product Model",
                "x": 0.5,
                "xanchor": "center"
            },
            xaxis_title="Product Model",
            yaxis_title="Number of Reviews",
            barmode="stack",
            height=500,
            xaxis={"tickangle": -45}
        )
        
        return fig
    
    def create_top_features_chart(self, n: int = 10) -> go.Figure:
        """Create chart of top mentioned features."""
        top_features = self.analyzer.get_top_features(n=n)
        
        features = list(top_features.keys())
        counts = list(top_features.values())
        
        fig = go.Figure(data=[go.Bar(
            x=counts,
            y=features,
            orientation="h",
            marker_color="#3498db",
            text=counts,
            textposition="outside"
        )])
        
        fig.update_layout(
            title={
                "text": f"Top {n} Most Mentioned Features",
                "x": 0.5,
                "xanchor": "center"
            },
            xaxis_title="Number of Mentions",
            yaxis_title="Feature",
            height=500
        )
        
        return fig
    
    def create_sentiment_timeline(self) -> go.Figure:
        """Create timeline of sentiment over time (if date data available)."""
        # Check if we have date information
        if "PublishedAt" not in self.df.columns:
            # Try to merge with clean_stage_1.csv for dates
            try:
                from config import INTERMEDIATE_DATA_DIR
                clean_df = pd.read_csv(INTERMEDIATE_DATA_DIR / "clean_stage_1.csv")
                if "PublishedAt" in clean_df.columns:
                    # Merge on comment_id if possible
                    self.df = self.df.merge(
                        clean_df[["PublishedAt"]],
                        left_index=True,
                        right_index=True,
                        how="left"
                    )
            except:
                pass
        
        if "PublishedAt" not in self.df.columns:
            logger.warning("No date information available for timeline")
            return None
        
        # Parse dates and aggregate
        self.df["date"] = pd.to_datetime(self.df["PublishedAt"], errors="coerce")
        self.df = self.df.dropna(subset=["date"])
        
        daily_sentiment = self.df.groupby([self.df["date"].dt.date, "sentiment"]).size().unstack(fill_value=0)
        
        fig = go.Figure()
        
        colors = {"positive": "#2ecc71", "negative": "#e74c3c", "neutral": "#95a5a6"}
        for sentiment in ["positive", "neutral", "negative"]:
            if sentiment in daily_sentiment.columns:
                fig.add_trace(go.Scatter(
                    x=daily_sentiment.index,
                    y=daily_sentiment[sentiment],
                    mode="lines+markers",
                    name=sentiment.capitalize(),
                    line=dict(color=colors[sentiment], width=2),
                    marker=dict(size=6)
                ))
        
        fig.update_layout(
            title={
                "text": "Sentiment Trends Over Time",
                "x": 0.5,
                "xanchor": "center"
            },
            xaxis_title="Date",
            yaxis_title="Number of Reviews",
            height=400,
            hovermode="x unified"
        )
        
        return fig
    
    def create_comprehensive_dashboard(self) -> go.Figure:
        """Create comprehensive dashboard with all visualizations."""
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                "Overall Sentiment Distribution",
                "Sentiment Score by Feature",
                "Feature Sentiment Heatmap",
                "Model Comparison",
                "Top Features",
                "Sentiment Trends"
            ),
            specs=[
                [{"type": "pie"}, {"type": "bar"}],
                [{"type": "heatmap"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "bar"}]
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )
        
        # 1. Sentiment Distribution (Pie)
        sentiment_counts = self.df["sentiment"].value_counts()
        colors = {"positive": "#2ecc71", "negative": "#e74c3c", "neutral": "#95a5a6"}
        fig.add_trace(
            go.Pie(
                labels=sentiment_counts.index,
                values=sentiment_counts.values,
                hole=0.4,
                marker=dict(colors=[colors.get(s, "#95a5a6") for s in sentiment_counts.index]),
                textinfo="label+percent"
            ),
            row=1, col=1
        )
        
        # 2. Feature Sentiment Scores (Bar)
        feature_sentiments = self.analyzer.get_feature_sentiments()
        features = list(feature_sentiments.keys())
        scores = [feature_sentiments[f]["sentiment_score"] for f in features]
        sorted_data = sorted(zip(features, scores), key=lambda x: x[1], reverse=True)
        features, scores = zip(*sorted_data)
        colors_bar = ["#2ecc71" if s > 0 else "#e74c3c" if s < 0 else "#95a5a6" for s in scores]
        
        fig.add_trace(
            go.Bar(x=list(features)[:10], y=list(scores)[:10], marker_color=colors_bar[:10]),
            row=1, col=2
        )
        
        # 3. Feature Sentiment Heatmap (row 2, col 1)
        pivot = pd.crosstab(self.df["feature"], self.df["sentiment"], normalize="index") * 100
        pivot = pivot[["positive", "neutral", "negative"]]
        
        fig.add_trace(
            go.Heatmap(
                z=pivot.values,
                x=pivot.columns,
                y=pivot.index,
                colorscale=[[0, "#e74c3c"], [0.5, "#95a5a6"], [1, "#2ecc71"]],
                showscale=True
            ),
            row=2, col=1
        )
        
        # 4. Model Comparison (row 2, col 2)
        model_sentiments = self.analyzer.get_model_sentiments()
        models = list(model_sentiments.keys())
        positive = [model_sentiments[m]["positive"] for m in models]
        negative = [model_sentiments[m]["negative"] for m in models]
        
        fig.add_trace(
            go.Bar(name="Positive", x=models, y=positive, marker_color="#2ecc71"),
            row=2, col=2
        )
        fig.add_trace(
            go.Bar(name="Negative", x=models, y=negative, marker_color="#e74c3c"),
            row=2, col=2
        )
        
        # 5. Top Features (row 3, col 1)
        top_features = self.analyzer.get_top_features(n=10)
        fig.add_trace(
            go.Bar(
                x=list(top_features.values()),
                y=list(top_features.keys()),
                orientation="h",
                marker_color="#3498db"
            ),
            row=3, col=1
        )
        
        # 6. Sentiment Timeline (row 3, col 2) - if available
        timeline_fig = self.create_sentiment_timeline()
        if timeline_fig and timeline_fig.data:
            for trace in timeline_fig.data:
                fig.add_trace(trace, row=3, col=2)
        
        # Update layout
        fig.update_layout(
            title_text="Redmi Sentiment Analysis Dashboard",
            title_x=0.5,
            height=1400,
            showlegend=True
        )
        
        # Update axes
        fig.update_xaxes(title_text="Sentiment Score", row=1, col=2)
        fig.update_xaxes(title_text="Sentiment", row=2, col=1)
        fig.update_xaxes(title_text="Count", row=2, col=2)
        fig.update_xaxes(title_text="Mentions", row=3, col=1)
        if timeline_fig and timeline_fig.data:
            fig.update_xaxes(title_text="Date", row=3, col=2)
        
        fig.update_yaxes(title_text="Feature", row=1, col=2)
        fig.update_yaxes(title_text="Feature", row=2, col=1)
        fig.update_yaxes(title_text="Model", row=2, col=2)
        fig.update_yaxes(title_text="Feature", row=3, col=1)
        if timeline_fig and timeline_fig.data:
            fig.update_yaxes(title_text="Count", row=3, col=2)
        
        return fig
    
    def save_dashboard(self, output_path: Path = None, format: str = "html") -> Path:
        """
        Save dashboard to file.
        
        Args:
            output_path: Output file path
            format: Output format (html, json, png, pdf)
        """
        if output_path is None:
            output_dir = Path(__file__).parent.parent / "data" / "dashboards"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"sentiment_dashboard.{format}"
        
        fig = self.create_comprehensive_dashboard()
        
        if format == "html":
            fig.write_html(str(output_path))
        elif format == "json":
            fig.write_json(str(output_path))
        elif format == "png":
            fig.write_image(str(output_path), width=1920, height=1080)
        elif format == "pdf":
            fig.write_image(str(output_path), format="pdf", width=1920, height=1080)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"[OK] Dashboard saved to: {output_path}")
        return output_path
    
    def show_dashboard(self) -> None:
        """Display dashboard in browser."""
        fig = self.create_comprehensive_dashboard()
        fig.show()


def main():
    """Generate and display dashboard."""
    import sys
    import webbrowser
    import os
    
    logging.basicConfig(level=logging.INFO)
    
    try:
        dashboard = SentimentDashboard()
        output_path = dashboard.save_dashboard(format="html")
        logger.info("[OK] Dashboard generated successfully!")
        
        # Get the full path
        if isinstance(output_path, str):
            output_path = Path(output_path)
        full_path = output_path.resolve()
        
        logger.info(f"[OK] Dashboard saved to: {full_path}")
        logger.info("Opening dashboard in browser...")
        
        # Open in default browser (Windows path format)
        try:
            # Convert Windows path to file:// URL format
            file_url = full_path.as_uri()
            webbrowser.open(file_url)
            logger.info("[OK] Dashboard opened in browser!")
        except Exception as e:
            logger.warning(f"[WARNING] Could not auto-open browser: {e}")
            logger.info(f"Please manually open this file in your browser:")
            logger.info(f"  {full_path}")
        
    except Exception as e:
        logger.error(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
