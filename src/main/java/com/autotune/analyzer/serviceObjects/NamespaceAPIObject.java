package com.autotune.analyzer.serviceObjects;

import com.autotune.analyzer.recommendations.NamespaceRecommendations;
import com.autotune.common.data.metrics.Metric;
import com.autotune.utils.KruizeConstants;
import com.google.gson.annotations.SerializedName;

import java.util.List;

/**
 * This NamespaceAPIObject class simulates the NamespaceData class for the create experiment and list experiment API
 */
public class NamespaceAPIObject {
    @SerializedName(KruizeConstants.JSONKeys.NAMESPACE_NAME)
    private String namespaceName;
    @SerializedName(KruizeConstants.JSONKeys.RECOMMENDATIONS)
    private NamespaceRecommendations namespaceRecommendations;
    private List<Metric> metrics;

    public NamespaceAPIObject(String namespaceName, NamespaceRecommendations namespaceRecommendations, List<Metric> metrics) {
        this.namespaceName = namespaceName;
        this.namespaceRecommendations = namespaceRecommendations;
        this.metrics = metrics;
    }

    public NamespaceAPIObject() {
    }

    /**
     * Returns the name of the namespace
     * @return String containing the name of the namespace
     */
    public String getnamespace_name() {
        return namespaceName;
    }

    /**
     * Returns the recommendations object for the namespace
     * @return namespace recommendations object containing the recommendations for a namespace
     */
    public NamespaceRecommendations getnamespaceRecommendations() {
        return namespaceRecommendations;
    }

    /**
     * Returns the namespace related metrics
     * @return hashmap containing the namespace related metrics and metric name as a key
     */
    public List<Metric> getMetrics() {
        return metrics;
    }

    @Override
    public String toString() {
        return "NamespaceAPIObject{" +
                "namespaceName='" + namespaceName + '\'' +
                ", namespaceRecommendations=" + namespaceRecommendations +
                ", metrics=" + metrics +
                '}';
    }
}
