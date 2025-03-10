/*******************************************************************************
 * Copyright (c) 2021, 2022 Red Hat, IBM Corporation and others.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *******************************************************************************/

package com.autotune.common.utils;

import com.autotune.analyzer.recommendations.RecommendationConfigItem;
import com.autotune.common.datasource.DataSourceCollection;
import com.autotune.common.datasource.DataSourceInfo;
import com.autotune.common.datasource.DataSourceManager;

import com.autotune.utils.KruizeConstants;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.Timestamp;
import java.util.*;
import java.util.concurrent.TimeUnit;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * This Class holds the utilities needed by the classes in common package
 */
public class CommonUtils {

    private static final Logger LOGGER = LoggerFactory.getLogger(CommonUtils.class);

    /**
     * AutotuneDatasourceTypes is an ENUM which holds different types of
     * datasources supported by Autotune
     *
     * For now only Queryable and File based datasources are supported
     */
    public enum AutotuneDatasourceTypes {
        /**
         * If the datasource is queryable (datastore, database)
         */
        QUERYABLE,
        /**
         * If the datasource is file based (Cgroup files)
         */
        FILE,
    }

    /**
     * AddDataSourceStatus is an ENUM which holds the possible statuses
     * to return for adding a datasource to a collection in Autotune
     *
     * For now Success and Datasource not reachable are two possibilities
     * Failure status is parked as a placeholder for now to fit for an exact use case which might arise
     */
    public enum AddDataSourceStatus {
        SUCCESS,
        FAILURE,
        DATASOURCE_NOT_REACHABLE
    }

    /**
     * DatasourceReachabilityStatus is a ENUM which holds the possible statuses
     * to return for checking if a datasource is reachable
     *
     * REACHABLE - states that the datasource is reachable
     * NOT_REACHABLE - states that the datasource is not reachable
     */
    public enum DatasourceReachabilityStatus {
        REACHABLE,
        NOT_REACHABLE,
    }

    /**
     * DatasourceReliabilityStatus is a ENUM which holds the possible statuses
     * to return for checking if a datasource is reliable
     *
     * RELIABLE - states that the datasource is reliable
     * NOT_RELIABLE -  states that the datasource is not reliable
     */
    public enum DatasourceReliabilityStatus {
        /**
         * We set the status as Reliable if the datasource is up and running and it provides information
         */
        RELIABLE,
        /**
         * We set the status as Not Reliable if the datasource is up and not providing information
         */
        NOT_RELIABLE,
    }

    /**
     * QueryValidity is an ENUM which holds the possible validity status to be
     * returned after performing a query validation
     */
    public enum QueryValidity {
        // If the query check is done and the query is found to be valid
        VALID,
        // If the query is found to be having invalid parameters
        INVALID_PARAMS,
        // If the query is found to be having invalid time ranges
        INVALID_RANGE,
        // If the query itself is found to be invalid
        INVALID_QUERY,
        // If the query is empty
        EMPTY_QUERY,
        // If the query is null
        NULL_QUERY
    }

    /**
     * Extracts the time value (digits) from a time string
     * @param timestr
     * @return
     */
    public static int getTimeValue(String timestr) {
        String workingstr = timestr.replace(KruizeConstants.Patterns.WHITESPACE_PATTERN, "");
        Pattern pattern = Pattern.compile(KruizeConstants.Patterns.DURATION_PATTERN);
        Matcher matcher = pattern.matcher(workingstr);
        if (matcher.find()) {
            if (null != matcher.group(1)) {
                return Integer.parseInt(matcher.group(1));
            }
        }
        return Integer.MIN_VALUE;
    }

    /**
     * Extracts the time units (time measurement units eg: seconds, minutes etc)
     * from a time string
     * @param timestr
     * @return
     */
    public static TimeUnit getTimeUnit(String timestr) {
        String workingstr = timestr.replace(KruizeConstants.Patterns.WHITESPACE_PATTERN, "");
        Pattern pattern = Pattern.compile(KruizeConstants.Patterns.DURATION_PATTERN);
        Matcher matcher = pattern.matcher(workingstr);
        if (matcher.find()) {
            if (null != matcher.group(2).trim()) {
                String trimmedDurationUnit = matcher.group(2).trim();
                if (trimmedDurationUnit.equalsIgnoreCase(KruizeConstants.TimeUnitsExt.SECOND_SINGLE_LC)
                        || trimmedDurationUnit.equalsIgnoreCase(KruizeConstants.TimeUnitsExt.SECOND_SHORT_LC_SINGULAR)
                        || trimmedDurationUnit.equalsIgnoreCase(KruizeConstants.TimeUnitsExt.SECOND_SHORT_LC_PLURAL)
                        || trimmedDurationUnit.equalsIgnoreCase(KruizeConstants.TimeUnitsExt.SECOND_LC_SINGULAR)
                        || trimmedDurationUnit.equalsIgnoreCase(KruizeConstants.TimeUnitsExt.SECOND_LC_PLURAL)) {
                    return TimeUnit.SECONDS;
                }
                if (trimmedDurationUnit.equalsIgnoreCase(KruizeConstants.TimeUnitsExt.MINUTE_SINGLE_LC)
                        || trimmedDurationUnit.equalsIgnoreCase(KruizeConstants.TimeUnitsExt.MINUTE_SHORT_LC_SINGULAR)
                        || trimmedDurationUnit.equalsIgnoreCase(KruizeConstants.TimeUnitsExt.MINUTE_SHORT_LC_PLURAL)
                        || trimmedDurationUnit.equalsIgnoreCase(KruizeConstants.TimeUnitsExt.MINUTE_LC_SINGULAR)
                        || trimmedDurationUnit.equalsIgnoreCase(KruizeConstants.TimeUnitsExt.MINUTE_LC_PLURAL)) {
                    return TimeUnit.MINUTES;
                }
                if (trimmedDurationUnit.equalsIgnoreCase(KruizeConstants.TimeUnitsExt.HOUR_SINGLE_LC)
                        || trimmedDurationUnit.equalsIgnoreCase(KruizeConstants.TimeUnitsExt.HOUR_SHORT_LC_SINGULAR)
                        || trimmedDurationUnit.equalsIgnoreCase(KruizeConstants.TimeUnitsExt.HOUR_SHORT_LC_PLURAL)
                        || trimmedDurationUnit.equalsIgnoreCase(KruizeConstants.TimeUnitsExt.HOUR_LC_SINGULAR)
                        || trimmedDurationUnit.equalsIgnoreCase(KruizeConstants.TimeUnitsExt.HOUR_LC_PLURAL)) {
                    return TimeUnit.HOURS;
                }
            }
        }
        return null;
    }

    /**
     * Returns the short string representation of a time unit
     * @param timeUnit
     * @return
     */
    public static String getShortRepOfTimeUnit(TimeUnit timeUnit) {
        if (timeUnit.equals(TimeUnit.HOURS))
            return KruizeConstants.TimeUnitsExt.HOUR_SINGLE_LC;
        if (timeUnit.equals(TimeUnit.MINUTES))
            return KruizeConstants.TimeUnitsExt.MINUTE_SINGLE_LC;
        if (timeUnit.equals(TimeUnit.SECONDS))
            return KruizeConstants.TimeUnitsExt.SECOND_SINGLE_LC;
        return null;
    }


    /**
     * Converts the time unit to seconds
     * @param unit
     * @return
     */
    public static int getTimeUnitInSeconds(TimeUnit unit) {
        if (unit.equals(TimeUnit.SECONDS)) {
            return 1;
        } else if (unit.equals(TimeUnit.MINUTES)) {
            return KruizeConstants.TimeConv.NO_OF_SECONDS_PER_MINUTE;
        } else if (unit.equals(TimeUnit.HOURS)) {
            return KruizeConstants.TimeConv.NO_OF_MINUTES_PER_HOUR * KruizeConstants.TimeConv.NO_OF_SECONDS_PER_MINUTE;
        } else {
            return Integer.MIN_VALUE;
        }
    }

    /**
     * Checks if the query has a time range
     * @param query
     * @return
     */
    public static boolean checkIfQueryHasTimeRange(String query) {
        String workingstr = query.replace(KruizeConstants.Patterns.WHITESPACE_PATTERN, "");
        Pattern pattern = Pattern.compile(KruizeConstants.Patterns.QUERY_WITH_TIME_RANGE_PATTERN);
        Matcher matcher = pattern.matcher(workingstr);
        if (matcher.find()) {
            return true;
        }
        return false;
    }

    /**
     * Extracts the time range from a query
     * @param query
     * @return
     */
    public static String extractTimeUnitFromQuery(String query) {
        String timeContent = query.substring(query.lastIndexOf('[') + 1);
        timeContent = timeContent.substring(0, timeContent.indexOf(']'));
        return timeContent;
    }

    /**
     * Checks if two time strings represent same time
     * @param timeStrOne
     * @param timeStrTwo
     * @return
     */
    public static boolean checkTimeMatch(String timeStrOne, String timeStrTwo) {
        int timeStrOneTimeValue = CommonUtils.getTimeValue(timeStrOne);
        TimeUnit timeStrOneTimeUnit = CommonUtils.getTimeUnit(timeStrOne);
        int timeStrTwoTimeValue = CommonUtils.getTimeValue(timeStrTwo);
        TimeUnit timeStrTwoTimeUnit = CommonUtils.getTimeUnit(timeStrTwo);
        if (Integer.MIN_VALUE != timeStrOneTimeValue
                && Integer.MIN_VALUE != timeStrTwoTimeValue
                && null != timeStrOneTimeUnit
                && null != timeStrTwoTimeUnit) {
            return timeStrOneTimeValue * getTimeUnitInSeconds(timeStrOneTimeUnit) == timeStrTwoTimeValue * getTimeUnitInSeconds(timeStrTwoTimeUnit);
        }
        return false;
    }

    /**
     * Get the base datasource URL for running query
     * @param dataSourceInfo
     * @param datasource
     * @return
     */
    public static String getBaseDataSourceUrl(DataSourceInfo dataSourceInfo, String datasource) {
        if (datasource.equalsIgnoreCase(KruizeConstants.SupportedDatasources.PROMETHEUS)) {
            return (new StringBuilder())
                    .append(dataSourceInfo.getUrl().toString())
                    .append(dataSourceInfo.getUrl().toString().endsWith("/") ? "" : "/")
                    .append("api/v1/query?query=")
                    .toString();
        }
        return null;
    }

    public static int getTimeToSleepMillis(int timeValue, TimeUnit timeUnit) {
        if (null == timeUnit)
            return 0;
        if (timeValue < 0)
            timeValue = -1 * timeValue;
        if (timeValue == 0)
            return 0;
        int secsInUnit = getTimeUnitInSeconds(timeUnit);
        if (secsInUnit == Integer.MIN_VALUE)
            return 0;
        return timeValue * secsInUnit * KruizeConstants.TimeConv.NO_OF_MSECS_IN_SEC;
    }

    public static Timestamp addDays(Timestamp date, int days) {
        Calendar cal = Calendar.getInstance();
        cal.setTime(date);
        cal.add(Calendar.DATE, days);
        return new Timestamp(cal.getTime().getTime());
    }

    public static Double percentile(double percentile, List<Double> items) {
        Collections.sort(items);
        return items.get((int) Math.round(percentile / 100.0 * (items.size() - 1)));
    }

    public static double getPercentage(double newer, double older) {
        if (older == 0)
            return 0.0;

        return ((newer - older)/older) * 100;
    }

    public static DataSourceInfo getDataSourceInfo(String dataSourceName) throws Exception {
        DataSourceManager dataSourceManager = new DataSourceManager();
        // fetch the datasource from the config file first
        DataSourceInfo datasource = DataSourceCollection.getInstance().getDataSourcesCollection().get(dataSourceName);
        if (isInvalidDataSource(datasource)) {
            // fetch the datasource from the DB
            datasource = dataSourceManager.fetchDataSourceFromDBByName(dataSourceName);
            if (isInvalidDataSource(datasource)) {
                throw new Exception(KruizeConstants.DataSourceConstants.DataSourceErrorMsgs.INVALID_DATASOURCE_INFO + dataSourceName);
            }
        }
        return datasource;
    }

    // Helper method to validate the DataSourceInfo object
    public static boolean isInvalidDataSource(DataSourceInfo datasource) {
        return datasource == null || datasource.getAuthenticationConfig() == null ||
                datasource.getAuthenticationConfig().toString().isEmpty();
    }

    public static RecommendationConfigItem formatMemoryUnits(RecommendationConfigItem input) {
        if (input == null) {
            return new RecommendationConfigItem(KruizeConstants.ErrorMsgs.RecommendationErrorMsgs.INPUT_NULL);
        }

        Double amount = input.getAmount();
        String format = input.getFormat();

        if (amount == null || format == null) {
            return new RecommendationConfigItem(KruizeConstants.ErrorMsgs.RecommendationErrorMsgs.AMT_FORMAT_IS_NULL);
        }

        if (amount < 0) {
            return new RecommendationConfigItem(KruizeConstants.ErrorMsgs.RecommendationErrorMsgs.VALUE_NEGATIVE);
        }

        // Convert all formats to bytes
        double bytes = convertToBytes(amount, format);

        if (bytes < 0) {
            return new RecommendationConfigItem(KruizeConstants.ErrorMsgs.RecommendationErrorMsgs.INVALID_MEM_FORMAT);
        }

        // Determine the best unit for the value
        String[] units = {"bytes", "Ki", "Mi", "Gi", "Ti", "Pi"};
        int unitIndex = 0;

        while (bytes >= 1024 && unitIndex < units.length - 1) {
            bytes /= 1024;
            unitIndex++;
        }

        // Create a new RecommendationConfigItem with the formatted result
        return new RecommendationConfigItem(bytes, units[unitIndex]);
    }

    public static RecommendationConfigItem formatCpuUnits(RecommendationConfigItem configItem) {
        if (configItem == null || configItem.getAmount() == null || configItem.getFormat() == null) {
            return new RecommendationConfigItem(KruizeConstants.ErrorMsgs.RecommendationErrorMsgs.AMT_FORMAT_IS_NULL);
        }

        String format = configItem.getFormat().toLowerCase();
        Double amount = configItem.getAmount();

        if ("cores".equals(format)) {
            // Convert cores to milli (m) by multiplying by 1000 and rounding to the nearest whole number
            double convertedAmount = Math.round(amount * 1000);
            return new RecommendationConfigItem(convertedAmount, "m");
        }

        // If the format is not "cores", return the same object with an error message
        return new RecommendationConfigItem(KruizeConstants.ErrorMsgs.RecommendationErrorMsgs.CPU_UNSUPPORTED_FORMAT + format);
    }

    public static RecommendationConfigItem formatAcceleratorUnits(RecommendationConfigItem configItem) {
        if (configItem == null || configItem.getAmount() == null || configItem.getFormat() == null) {
            return new RecommendationConfigItem(KruizeConstants.ErrorMsgs.RecommendationErrorMsgs.AMT_FORMAT_IS_NULL);
        }

        String format = configItem.getFormat().toLowerCase();
        Double amount = configItem.getAmount();

        if ("cores".equals(format)) {
            return new RecommendationConfigItem(amount, "");
        }

        // If the format is not "cores", return the same object with an error message
        return new RecommendationConfigItem(KruizeConstants.ErrorMsgs.RecommendationErrorMsgs.ACCELERATOR_UNSUPPORTED_FORMAT + format);
    }


    public static double convertToBytes(double amount, String format) {
        format = format.toLowerCase();

        return switch (format) {
            case "bytes", "byte" -> amount;
            case "kb", "kilobyte", "kilobytes" -> amount * 1000;
            case "kib", "kibibyte", "kibibytes" -> amount * 1024;
            case "mb", "megabyte", "megabytes" -> amount * 1000 * 1000;
            case "mib", "mebibyte", "mebibytes" -> amount * 1024 * 1024;
            case "gb", "gigabyte", "gigabytes" -> amount * 1000 * 1000 * 1000;
            case "gib", "gibibyte", "gibibytes" -> amount * 1024 * 1024 * 1024;
            case "tb", "terabyte", "terabytes" -> amount * 1000 * 1000 * 1000 * 1000;
            case "tib", "tebibyte", "tebibytes" -> amount * 1024 * 1024 * 1024 * 1024;
            default -> -1; // unsupported format
        };
    }
}
