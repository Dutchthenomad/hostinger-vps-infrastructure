# Solana Bundler Detector

A foundation for building token transaction analysis tools on Solana. Provides basic bundling detection metrics with an extensible architecture for custom analysis requirements.

## What It Analyzes

The tool examines token transaction patterns through four core metrics:

### Timing Cluster Analysis (40% weight)

Identifies transactions occurring within suspicious time windows (30s, 1min, 5min). Groups consecutive transactions and scores based on cluster size relative to total transactions. High scores indicate potential bot or bundler coordination.

### Wallet Similarity Detection (30% weight)

Analyzes behavioral patterns across wallets by examining transaction frequency distributions. Calculates coefficient of variation in transaction counts - lower variation suggests coordinated behavior from potentially related wallets.

### Transaction Size Patterns (20% weight)

Detects automated buying through transaction amount analysis. Examines variance in transaction sizes and flags suspiciously similar amounts that suggest preset bot parameters rather than organic trading.

### Token Distribution Concentration (10% weight)

Measures wealth concentration using Gini coefficient calculations. Evaluates how token holdings are distributed among buyers to identify potential accumulation strategies.

## Data Sources

- **Helius Enhanced Transactions API**: Primary source for parsed transaction data
- **Solana RPC**: Fallback for signature retrieval and basic account information
- **getAsset API**: Token metadata extraction for UI display

## Architecture

The codebase is structured for extensibility:

```
src/
├── lib/analyzer.ts          # Core analysis engine
├── components/              # Modular UI components
└── App.tsx                  # Main application logic
```

## Extending the Platform

This is intentionally a starting point. Token analysis requirements vary significantly based on:

- Market conditions and trading patterns
- Specific token economics and distribution mechanisms
- Evolving manipulation techniques
- Regulatory and compliance needs

### Adding New Metrics

1. Implement analysis function in `analyzer.ts`
2. Add metric to the `AnalysisResult` interface
3. Include weighting in the overall score calculation
4. Update UI components to display new insights

### Suggested Extensions

- **Liquidity pool manipulation detection**: Analyze LP token distribution and pool creation timing
- **Cross-DEX coordination**: Compare transaction patterns across different exchanges
- **Historical pattern matching**: Build databases of known manipulation signatures
- **Real-time monitoring**: Implement WebSocket connections for live analysis
- **Social sentiment integration**: Correlate on-chain activity with social metrics

## Technical Notes

- Uses batch processing to respect API rate limits
- Implements fallback mechanisms for data retrieval failures
- Modular component structure allows independent feature development
- Statistical analysis functions are isolated for easy modification

## Limitations

No analysis tool can detect all forms of coordination or manipulation. Sophisticated actors will always adapt techniques to circumvent detection. This tool provides a foundation for understanding basic patterns, but effective analysis requires:

- Regular metric refinement based on observed attack vectors
- Domain-specific customization for different token types
- Integration with multiple data sources and analysis techniques
- Continuous monitoring and pattern database updates

The goal is not comprehensive detection but rather a starting point for building tailored analysis solutions.

## Setup

1. Clone the repository
2. Install dependencies: `npm install`
3. Get a free Helius API key from [dashboard.helius.dev](https://dashboard.helius.dev/api-keys)
4. Configure API key in the settings panel
5. Run development server: `npm run dev`

Built with React, TypeScript, and Tailwind CSS.
