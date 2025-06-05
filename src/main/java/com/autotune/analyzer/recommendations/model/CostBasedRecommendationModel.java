package com.autotune.analyzer.recommendations.model;

import com.autotune.analyzer.recommendations.RecommendationConstants;

public class CostBasedRecommendationModel extends GenericRecommendationModel {

    public static final String defaultName = RecommendationConstants.RecommendationEngine.ModelNames.COST;

    public CostBasedRecommendationModel(RecommendationTunables recommendationTunables) {
        super( defaultName, recommendationTunables );
    }
}