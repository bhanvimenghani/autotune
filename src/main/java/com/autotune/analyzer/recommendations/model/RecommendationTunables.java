package com.autotune.analyzer.recommendations.model;

import com.autotune.utils.KruizeConstants;
import com.google.gson.annotations.SerializedName;

/**
 * This Represents tunable parameters for generating recommendations.
 * This class stores percentile values for memory, CPU, and accelerator utilization.
 * These tunables are used to fine-tune the recommendations generated by the system.
 */
public class RecommendationTunables {

    @SerializedName(KruizeConstants.JSONKeys.MEMORY_PERCENTILE)
    protected double memoryPercentile;

    @SerializedName(KruizeConstants.JSONKeys.CPU_PERCENTILE)
    protected double cpuPercentile;

    @SerializedName(KruizeConstants.JSONKeys.ACCELERATOR_PERCENTILE)
    protected double acceleratorPercentile;


    public RecommendationTunables(double CPU_PERCENTILE, double MEMORY_PERCENTILE, double ACCELERATOR_PERCENTILE) {
        this.cpuPercentile = CPU_PERCENTILE;
        this.memoryPercentile = MEMORY_PERCENTILE;
        this.acceleratorPercentile = ACCELERATOR_PERCENTILE;
    }

    @Override
    public String toString() {
        return "RecommendationTunable{" +
                "cpu=" + cpuPercentile +
                ", memory=" + memoryPercentile +
                ", accelerator=" + acceleratorPercentile +
                '}';
    }

    public double getMemoryPercentile() {
        return memoryPercentile;
    }

    public void setMemoryPercentile(double memory_percentile) {
        this.memoryPercentile = memory_percentile;
    }

    public double getCpuPercentile() {
        return cpuPercentile;
    }

    public void setCpuPercentile(double cpu_percentile) {
        this.cpuPercentile = cpu_percentile;
    }

    public double getAcceleratorPercentile() {
        return acceleratorPercentile;
    }

    public void setAcceleratorPercentile(double accelerator_percentile) {
        this.acceleratorPercentile = accelerator_percentile;
    }
}
