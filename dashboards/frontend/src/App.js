import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  TextField,
  Button,
  Card,
  CardContent,
  Chip,
  IconButton,
  Snackbar,
  Collapse,
  Fab,
} from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import CloseIcon from '@mui/icons-material/Close';
import DownloadIcon from '@mui/icons-material/Download';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import TableChartIcon from '@mui/icons-material/TableChart';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import Plot from 'react-plotly.js';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './App.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Data states
  const [overallSentiment, setOverallSentiment] = useState(null);
  const [featureSentiments, setFeatureSentiments] = useState(null);
  const [modelSentiments, setModelSentiments] = useState(null);
  const [topFeatures, setTopFeatures] = useState(null);
  const [sentimentTimeline, setSentimentTimeline] = useState(null);
  
  // RAG states (tab)
  const [ragQuery, setRagQuery] = useState('');
  const [ragAnswer, setRagAnswer] = useState(null);
  const [ragLoading, setRagLoading] = useState(false);

  // Floating chat pop-up
  const [chatOpen, setChatOpen] = useState(false);
  const [floatQuery, setFloatQuery] = useState('');
  const [floatAnswer, setFloatAnswer] = useState(null);
  const [floatLoading, setFloatLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);

  // Reports & Alerts
  const [reportLoading, setReportLoading] = useState(null); // 'pdf' | 'excel' | null
  const [alertsLoading, setAlertsLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [overall, features, models, top, timeline] = await Promise.all([
        axios.get(`${API_BASE}/api/overall-sentiment`),
        axios.get(`${API_BASE}/api/feature-sentiments`),
        axios.get(`${API_BASE}/api/model-sentiments`),
        axios.get(`${API_BASE}/api/top-features?n=10`),
        axios.get(`${API_BASE}/api/sentiment-timeline`)
      ]);

      setOverallSentiment(overall.data);
      setFeatureSentiments(features.data);
      setModelSentiments(models.data);
      setTopFeatures(top.data);
      setSentimentTimeline(timeline.data?.available ? timeline.data : null);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRagQuery = async () => {
    if (!ragQuery.trim()) return;

    try {
      setRagLoading(true);
      const response = await axios.post(`${API_BASE}/api/rag/query`, {
        question: ragQuery,
        k: 5
      });
      setRagAnswer(response.data);
    } catch (err) {
      setError(err.message);
      console.error('RAG query error:', err);
    } finally {
      setRagLoading(false);
    }
  };

  const handleFloatQuery = async () => {
    const q = floatQuery.trim();
    if (!q) return;
    try {
      setFloatLoading(true);
      setFloatAnswer(null);
      const response = await axios.post(`${API_BASE}/api/rag/query`, { question: q, k: 5 });
      const data = response.data;
      setFloatAnswer(data);
      setChatHistory((prev) => [...prev, { question: q, answer: data }]);
    } catch (err) {
      setSnackbar({ open: true, message: err.response?.data?.detail || err.message, severity: 'error' });
    } finally {
      setFloatLoading(false);
    }
  };

  const handleDownloadReport = async (format) => {
    try {
      setReportLoading(format);
      const res = await axios.get(`${API_BASE}/api/reports/${format}`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement('a');
      a.href = url;
      a.setAttribute('download', res.headers['content-disposition']?.split('filename=')[1]?.replace(/"/g, '') || `sentiment_report.${format === 'pdf' ? 'pdf' : 'xlsx'}`);
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      setSnackbar({ open: true, message: `${format.toUpperCase()} report downloaded`, severity: 'success' });
    } catch (err) {
      setSnackbar({ open: true, message: err.response?.data?.detail || err.message, severity: 'error' });
    } finally {
      setReportLoading(null);
    }
  };

  const handleCheckAlerts = async () => {
    try {
      setAlertsLoading(true);
      const res = await axios.post(`${API_BASE}/api/alerts/check`, { send_email: false });
      const count = res.data?.count ?? 0;
      setSnackbar({
        open: true,
        message: count > 0 ? `${count} alert(s) detected. Check console or email if configured.` : 'No sentiment spikes or trend shifts detected.',
        severity: count > 0 ? 'warning' : 'success',
      });
    } catch (err) {
      setSnackbar({ open: true, message: err.response?.data?.detail || err.message, severity: 'error' });
    } finally {
      setAlertsLoading(false);
    }
  };

  const createSentimentPieChart = () => {
    if (!overallSentiment) return null;

    return {
      data: [{
        labels: ['Positive', 'Negative', 'Neutral'],
        values: [
          overallSentiment.positive,
          overallSentiment.negative,
          overallSentiment.neutral
        ],
        type: 'pie',
        hole: 0.4,
        marker: {
          colors: ['#2ecc71', '#e74c3c', '#95a5a6']
        }
      }],
      layout: {
        title: 'Overall Sentiment Distribution',
        height: 400
      }
    };
  };

  const createFeatureSentimentChart = () => {
    if (!featureSentiments) return null;

    const features = Object.keys(featureSentiments);
    const scores = features.map(f => featureSentiments[f].sentiment_score);
    
    const sorted = features
      .map((f, i) => ({ feature: f, score: scores[i] }))
      .sort((a, b) => b.score - a.score)
      .slice(0, 10);

    return {
      data: [{
        x: sorted.map(s => s.feature),
        y: sorted.map(s => s.score),
        type: 'bar',
        marker: {
          color: sorted.map(s => 
            s.score > 0 ? '#2ecc71' : s.score < 0 ? '#e74c3c' : '#95a5a6'
          )
        }
      }],
      layout: {
        title: 'Sentiment Score by Feature',
        xaxis: { title: 'Feature' },
        yaxis: { title: 'Sentiment Score (-1 to +1)', range: [-1, 1] },
        height: 400
      }
    };
  };

  const createModelComparisonChart = () => {
    if (!modelSentiments) return null;

    const models = Object.keys(modelSentiments);
    const positive = models.map(m => modelSentiments[m].positive);
    const negative = models.map(m => modelSentiments[m].negative);
    const neutral = models.map(m => modelSentiments[m].neutral);

    return {
      data: [
        { name: 'Positive', x: models, y: positive, type: 'bar', marker: { color: '#2ecc71' } },
        { name: 'Neutral', x: models, y: neutral, type: 'bar', marker: { color: '#95a5a6' } },
        { name: 'Negative', x: models, y: negative, type: 'bar', marker: { color: '#e74c3c' } }
      ],
      layout: {
        title: 'Sentiment Distribution by Product Model',
        barmode: 'stack',
        xaxis: { title: 'Product Model' },
        yaxis: { title: 'Number of Reviews' },
        height: 400
      }
    };
  };

  const createTopFeaturesChart = () => {
    if (!topFeatures) return null;

    const features = Object.keys(topFeatures);
    const counts = features.map(f => topFeatures[f]);

    return {
      data: [{
        x: counts,
        y: features,
        type: 'bar',
        orientation: 'h',
        marker: { color: '#3498db' }
      }],
      layout: {
        title: 'Top 10 Most Mentioned Features',
        xaxis: { title: 'Number of Mentions' },
        yaxis: { title: 'Feature' },
        height: 400
      }
    };
  };

  const createFeatureHeatmapChart = () => {
    if (!featureSentiments) return null;
    const sentiments = ['positive', 'neutral', 'negative'];
    const features = Object.keys(featureSentiments);
    const z = features.map(f => {
      const t = featureSentiments[f].total || 1;
      return [
        Math.round((featureSentiments[f].positive / t) * 100),
        Math.round((featureSentiments[f].neutral / t) * 100),
        Math.round((featureSentiments[f].negative / t) * 100)
      ];
    });
    return {
      data: [{
        z,
        x: sentiments,
        y: features,
        type: 'heatmap',
        colorscale: [[0, '#e74c3c'], [0.5, '#95a5a6'], [1, '#2ecc71']],
        showscale: true
      }],
      layout: {
        title: 'Feature Sentiment Heatmap',
        xaxis: { title: 'Sentiment' },
        yaxis: { title: 'Feature' },
        height: 400 + features.length * 18
      }
    };
  };

  const createSentimentTrendsChart = () => {
    if (!sentimentTimeline || !sentimentTimeline.dates?.length) return null;
    const { dates, positive, negative, neutral } = sentimentTimeline;
    return {
      data: [
        { x: dates, y: positive, type: 'scatter', mode: 'lines+markers', name: 'Positive', line: { color: '#2ecc71' }, marker: { size: 6 } },
        { x: dates, y: neutral, type: 'scatter', mode: 'lines+markers', name: 'Neutral', line: { color: '#95a5a6' }, marker: { size: 6 } },
        { x: dates, y: negative, type: 'scatter', mode: 'lines+markers', name: 'Negative', line: { color: '#e74c3c' }, marker: { size: 6 } }
      ],
      layout: {
        title: 'Sentiment Trends Over Time',
        xaxis: { title: 'Date' },
        yaxis: { title: 'Count' },
        height: 400,
        hovermode: 'x unified'
      }
    };
  };

  if (loading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" className="app-container">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          Redmi Sentiment Analysis Dashboard
        </Typography>
        <Typography variant="subtitle1" align="center" color="text.secondary" gutterBottom>
          Interactive insights from product reviews
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ mb: 3 }}>
        <Tab label="Overview" />
        <Tab label="RAG Query" />
      </Tabs>

      {tabValue === 0 && (
        <Grid container spacing={3}>
          {/* Reports & Alerts toolbar */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2, display: 'flex', flexWrap: 'wrap', gap: 2, alignItems: 'center' }}>
              <Typography variant="subtitle2" color="text.secondary" sx={{ mr: 1 }}>
                Reports & Alerts
              </Typography>
              <Button
                variant="outlined"
                size="small"
                startIcon={reportLoading === 'pdf' ? <CircularProgress size={16} /> : <PictureAsPdfIcon />}
                onClick={() => handleDownloadReport('pdf')}
                disabled={!!reportLoading}
              >
                Export PDF
              </Button>
              <Button
                variant="outlined"
                size="small"
                startIcon={reportLoading === 'excel' ? <CircularProgress size={16} /> : <TableChartIcon />}
                onClick={() => handleDownloadReport('excel')}
                disabled={!!reportLoading}
              >
                Export Excel
              </Button>
              <Button
                variant="outlined"
                size="small"
                color="warning"
                startIcon={alertsLoading ? <CircularProgress size={16} /> : <WarningAmberIcon />}
                onClick={handleCheckAlerts}
                disabled={alertsLoading}
              >
                Check Alerts
              </Button>
            </Paper>
          </Grid>
          {/* Overall Sentiment */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              {overallSentiment && (
                <>
                  <Typography variant="h6" gutterBottom>
                    Overall Sentiment
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Chip 
                      label={`Score: ${overallSentiment.sentiment_score.toFixed(3)}`}
                      color={overallSentiment.sentiment_score > 0 ? 'success' : 'error'}
                      sx={{ mr: 1 }}
                    />
                    <Chip label={`Total: ${overallSentiment.total}`} />
                  </Box>
                  {createSentimentPieChart() && (
                    <Plot
                      data={createSentimentPieChart().data}
                      layout={createSentimentPieChart().layout}
                      style={{ width: '100%', height: '100%' }}
                    />
                  )}
                </>
              )}
            </Paper>
          </Grid>

          {/* Feature Sentiment Scores */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              {createFeatureSentimentChart() && (
                <>
                  <Typography variant="h6" gutterBottom>
                    Feature Sentiment Scores
                  </Typography>
                  <Plot
                    data={createFeatureSentimentChart().data}
                    layout={createFeatureSentimentChart().layout}
                    style={{ width: '100%', height: '100%' }}
                  />
                </>
              )}
            </Paper>
          </Grid>

          {/* Model Comparison */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              {createModelComparisonChart() && (
                <>
                  <Typography variant="h6" gutterBottom>
                    Model Comparison
                  </Typography>
                  <Plot
                    data={createModelComparisonChart().data}
                    layout={createModelComparisonChart().layout}
                    style={{ width: '100%', height: '100%' }}
                  />
                </>
              )}
            </Paper>
          </Grid>

          {/* Feature Sentiment Heatmap */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              {createFeatureHeatmapChart() && (
                <>
                  <Typography variant="h6" gutterBottom>
                    Feature Sentiment Heatmap
                  </Typography>
                  <Plot
                    data={createFeatureHeatmapChart().data}
                    layout={createFeatureHeatmapChart().layout}
                    style={{ width: '100%', height: '100%' }}
                  />
                </>
              )}
            </Paper>
          </Grid>

          {/* Sentiment Trends */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              {createSentimentTrendsChart() ? (
                <>
                  <Typography variant="h6" gutterBottom>
                    Sentiment Trends Over Time
                  </Typography>
                  <Plot
                    data={createSentimentTrendsChart().data}
                    layout={createSentimentTrendsChart().layout}
                    style={{ width: '100%', height: '100%' }}
                  />
                </>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Sentiment over time is shown when date data is available (e.g. from clean_stage_1.csv with PublishedAt).
                </Typography>
              )}
            </Paper>
          </Grid>

          {/* Top Features */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              {createTopFeaturesChart() && (
                <>
                  <Typography variant="h6" gutterBottom>
                    Top Features
                  </Typography>
                  <Plot
                    data={createTopFeaturesChart().data}
                    layout={createTopFeaturesChart().layout}
                    style={{ width: '100%', height: '100%' }}
                  />
                </>
              )}
            </Paper>
          </Grid>
        </Grid>
      )}

      {tabValue === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                RAG Query Interface
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Ask questions about product reviews and get AI-powered insights
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
                <TextField
                  fullWidth
                  label="Enter your question"
                  value={ragQuery}
                  onChange={(e) => setRagQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleRagQuery()}
                  placeholder="e.g., What are the main complaints about sound quality?"
                />
                <Button
                  variant="contained"
                  onClick={handleRagQuery}
                  disabled={ragLoading || !ragQuery.trim()}
                  sx={{ minWidth: 120 }}
                >
                  {ragLoading ? <CircularProgress size={24} /> : 'Query'}
                </Button>
              </Box>

              {ragAnswer && (
                <Card sx={{ mt: 2 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Answer
                    </Typography>
                    <Box className="markdown-content">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{ragAnswer.answer}</ReactMarkdown>
                    </Box>
                    
                    {ragAnswer.sources && ragAnswer.sources.length > 0 && (
                      <>
                        <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
                          Sources ({ragAnswer.sources.length})
                        </Typography>
                        {ragAnswer.sources.map((source, idx) => (
                          <Card key={idx} sx={{ mb: 1, bgcolor: 'grey.50' }}>
                            <CardContent>
                              <Typography variant="body2" color="text.secondary">
                                {source.metadata?.evidence || source.text}
                              </Typography>
                              <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                                <Chip 
                                  label={source.metadata?.feature || 'N/A'} 
                                  size="small" 
                                />
                                <Chip 
                                  label={source.metadata?.sentiment || 'N/A'} 
                                  size="small"
                                  color={
                                    source.metadata?.sentiment === 'positive' ? 'success' :
                                    source.metadata?.sentiment === 'negative' ? 'error' : 'default'
                                  }
                                />
                              </Box>
                            </CardContent>
                          </Card>
                        ))}
                      </>
                    )}
                  </CardContent>
                </Card>
              )}
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Floating RAG Chat pop-up */}
      <Box className="chat-float-wrapper">
        <Collapse in={chatOpen} collapsedSize={0} orientation="vertical">
          <Paper elevation={8} className="chat-float-panel">
            <Box className="chat-float-header">
              <Typography variant="subtitle1" fontWeight="bold">Ask about reviews</Typography>
              <IconButton size="small" onClick={() => setChatOpen(false)} aria-label="Close">
                <CloseIcon />
              </IconButton>
            </Box>
            <Box className="chat-float-body">
              {floatAnswer && (
                <Card sx={{ mb: 2, bgcolor: 'grey.50' }}>
                  <CardContent>
                    <Box className="markdown-content">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{floatAnswer.answer}</ReactMarkdown>
                    </Box>
                    {floatAnswer.sources?.length > 0 && (
                      <Typography variant="caption" color="text.secondary">
                        {floatAnswer.sources.length} source(s)
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              )}
              <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                <TextField
                  size="small"
                  fullWidth
                  placeholder="e.g. What do users say about battery?"
                  value={floatQuery}
                  onChange={(e) => setFloatQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleFloatQuery()}
                />
                <Button
                  variant="contained"
                  onClick={handleFloatQuery}
                  disabled={floatLoading || !floatQuery.trim()}
                  sx={{ minWidth: 90 }}
                >
                  {floatLoading ? <CircularProgress size={22} /> : 'Ask'}
                </Button>
              </Box>
            </Box>
          </Paper>
        </Collapse>
        <Fab
          color="primary"
          className="chat-float-fab"
          onClick={() => setChatOpen((o) => !o)}
          aria-label="Open RAG query"
        >
          <ChatIcon />
        </Fab>
      </Box>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={5000}
        onClose={() => setSnackbar((s) => ({ ...s, open: false }))}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setSnackbar((s) => ({ ...s, open: false }))} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
}

export default App;
