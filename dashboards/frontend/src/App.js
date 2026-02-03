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
  Chip
} from '@mui/material';
import Plot from 'react-plotly.js';
import axios from 'axios';
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
  
  // RAG states
  const [ragQuery, setRagQuery] = useState('');
  const [ragAnswer, setRagAnswer] = useState(null);
  const [ragLoading, setRagLoading] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [overall, features, models, top] = await Promise.all([
        axios.get(`${API_BASE}/api/overall-sentiment`),
        axios.get(`${API_BASE}/api/feature-sentiments`),
        axios.get(`${API_BASE}/api/model-sentiments`),
        axios.get(`${API_BASE}/api/top-features?n=10`)
      ]);

      setOverallSentiment(overall.data);
      setFeatureSentiments(features.data);
      setModelSentiments(models.data);
      setTopFeatures(top.data);
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
                    <Typography variant="body1" paragraph>
                      {ragAnswer.answer}
                    </Typography>
                    
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
    </Container>
  );
}

export default App;
