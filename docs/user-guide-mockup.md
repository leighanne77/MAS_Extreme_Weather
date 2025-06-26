# Pythia User Guide - Simplified Frontend

## Overview

Pythia is an AI-powered extreme weather risk assessment tool that helps capital market actors understand environmental risks and find nature-based resilience solutions. The frontend is designed to be simple and focused on displaying what our AI agents discover.

## Quick Start

### 1. Enter Your Query
- **Location**: Enter the specific location (city, county, or coordinates)
- **Query**: Ask about extreme weather risks, adaptation strategies, or financial impacts
- **Time Range**: Select 5, 7, or 10 years for analysis

### 2. Get Results
Pythia's AI agents will analyze your query and return:
- **Risk Assessment**: Overall risk level and breakdown by risk type
- **Resilience Options**: Nature-based and infrastructure solutions
- **ROI Analysis**: Financial impact and return on investment
- **Confidence Levels**: How certain the agents are about their analysis
- **Recommendations**: Specific actions to take

### 3. Export & Share
- Download results as JSON for integration with your systems
- Share insights with stakeholders
- Use data in your existing financial models

## Interface Components

### Query Section
```
┌─────────────────────────────────────────────────────────┐
│ Location: [Mobile Bay, Alabama]                         │
│ Query: [What are hurricane risks for manufacturing...] │
│ Time Range: [7 Years ▼]                                 │
│ [Analyze]                                               │
└─────────────────────────────────────────────────────────┘
```

**Tips:**
- Be specific about location (city, county, or coordinates)
- Ask about specific risks or adaptation strategies
- Include asset type when relevant (manufacturing, agriculture, etc.)

### Results Display

#### Risk Assessment Card
```
┌─────────────────────────────────────────────────────────┐
│ Risk Assessment                    [HIGH RISK]          │
│ Location: Mobile Bay, Alabama                           │
│ Time Period: 2026-2032                                  │
│ Analysis Date: January 15, 2025                         │
│                                                         │
│ Risk Breakdown:                                         │
│ • Hurricane Risk: [HIGH] Confidence: 85%               │
│ • Storm Surge Risk: [HIGH] Confidence: 90%             │
│ • Sea Level Rise: [MEDIUM] Confidence: 75%             │
└─────────────────────────────────────────────────────────┘
```

#### Resilience Options
```
┌─────────────────────────────────────────────────────────┐
│ Resilience Options (3 found)                           │
│                                                         │
│ 🌿 Mangrove Restoration                                │
│ ROI: 15.2% | Cost: $50K-$200K                          │
│ Reduces storm surge by 30-50%                          │
│                                                         │
│ 🏗️ Elevated Foundation Design                          │
│ ROI: 8.7% | Cost: $100K-$500K                          │
│ Protects against 2-3ft sea level rise                  │
│                                                         │
│ 💧 Rainwater Harvesting System                         │
│ ROI: 12.1% | Cost: $25K-$75K                           │
│ Reduces water dependency by 40%                        │
└─────────────────────────────────────────────────────────┘
```

#### ROI Analysis
```
┌─────────────────────────────────────────────────────────┐
│ ROI Analysis                                           │
│                                                         │
│ Asset Value: $2,500,000                                │
│ Risk Reduction: 35%                                    │
│ Annual Savings: $87,500                                │
│ Payback Period: 3.2 years                              │
│ NPV (7 years): $245,000                                │
└─────────────────────────────────────────────────────────┘
```

### Simple Filters
```
┌─────────────────────────────────────────────────────────┐
│ Filters:                                               │
│ Time: [All Time Periods ▼]                             │
│ Risk: [All Risk Levels ▼]                              │
│ Solutions: [All Solutions ▼]                           │
│ [Clear Filters]                                        │
└─────────────────────────────────────────────────────────┘
```

**Note:** Filters are basic - agents handle complex filtering based on your query.

### Charts Display
```
┌─────────────────────────────────────────────────────────┐
│ Charts                                                 │
│                                                         │
│ [Risk Assessment] [ROI Comparison] [Timeline]          │
│                                                         │
│ Risk Assessment Chart:                                 │
│ • Hurricane: HIGH (85%)                                │
│ • Storm Surge: HIGH (90%)                              │
│ • Sea Level Rise: MEDIUM (75%)                         │
└─────────────────────────────────────────────────────────┘
```

## Common Use Cases

### For Loan Officers
**Query Example:** "What are water scarcity risks for a farm loan in West Kansas over the next 7 years?"

**What You'll Get:**
- Collateral value risk assessment
- Default probability timeline
- Water management adaptation strategies
- ROI analysis for adaptation investments

### For Private Equity Investors
**Query Example:** "What are hurricane risks for a manufacturing facility in Mobile Bay and what adaptation strategies would protect the investment?"

**What You'll Get:**
- Asset value impact analysis
- Infrastructure adaptation options
- Cost-benefit analysis
- Timeline for implementation

### For Risk Officers
**Query Example:** "What are the portfolio-level extreme weather risks for our agricultural lending in the Midwest?"

**What You'll Get:**
- Portfolio risk distribution
- Capital allocation recommendations
- Stress testing scenarios
- Regulatory compliance insights

## Understanding Results

### Risk Levels
- **LOW**: Minimal impact expected
- **MEDIUM**: Moderate impact, monitoring recommended
- **HIGH**: Significant impact, action required
- **EXTREME**: Severe impact, immediate action needed

### Confidence Levels
- **95-99%**: Very high confidence
- **80-94%**: High confidence
- **60-79%**: Moderate confidence
- **40-59%**: Low confidence
- **<40%**: Very low confidence

### ROI Interpretation
- **Positive ROI**: Investment pays for itself
- **High ROI (>10%)**: Excellent investment opportunity
- **Moderate ROI (5-10%)**: Good investment with benefits
- **Low ROI (<5%)**: Consider other options

## Exporting Results

### JSON Export
Click the "Export" button to download a complete analysis including:
- Original query and parameters
- Risk assessment data
- Resilience options with costs and ROI
- Confidence levels and methodology
- Recommendations and timelines

### Integration
The JSON format is designed for easy integration with:
- Financial modeling tools
- Risk management systems
- Portfolio management platforms
- Reporting dashboards

## Troubleshooting

### Common Issues

**"No results found"**
- Check location spelling and format
- Try a broader location (county instead of city)
- Ensure query is specific enough

**"Analysis failed"**
- Check internet connection
- Try again in a few minutes
- Contact support if persistent

**"Low confidence results"**
- This is normal for emerging risks
- Consider multiple scenarios
- Focus on high-confidence aspects

### Getting Better Results

1. **Be Specific**: Include asset type, location, and time period
2. **Ask About Solutions**: Include "adaptation strategies" or "resilience options"
3. **Consider Multiple Scenarios**: Ask about different time periods
4. **Focus on ROI**: Include "financial impact" or "ROI" in queries

## Best Practices

### Query Formulation
✅ **Good:** "What are drought risks for a cattle operation in West Kansas over the next 7 years?"
❌ **Poor:** "What about weather?"

✅ **Good:** "What adaptation strategies would protect a data center from extreme heat in Phoenix?"
❌ **Poor:** "How to protect from heat?"

### Location Specification
✅ **Good:** "Mobile Bay, Alabama" or "Kansas City, Kansas"
❌ **Poor:** "The South" or "Kansas"

### Time Periods
- **5 Years**: Short-term planning and immediate risks
- **7 Years**: Standard investment horizon (recommended)
- **10 Years**: Long-term strategic planning

## Support

### Documentation
- This user guide
- API documentation (for developers)
- Case studies and examples

### Contact
- Technical support: support@pythia.com
- Feature requests: feedback@pythia.com
- Business inquiries: sales@pythia.com

---

**Remember:** Pythia's AI agents do the heavy lifting. The frontend is designed to simply display their insights in a clear, actionable format. Focus on asking good questions and interpreting the results for your specific needs. 