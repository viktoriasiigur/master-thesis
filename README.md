### Notes
  
* [Monte Carlo](https://machinelearningmastery.com/monte-carlo-sampling-for-probability/)
* [Bootstraping](https://builtin.com/data-science/bootstrapping-statistics)
* [Jackknifing](https://en.wikipedia.org/wiki/Jackknife_resampling)
* [Kriging](https://en.wikipedia.org/wiki/Kriging)


## Notes for Thesis

1. Sensors have anomaly of 11 minutes long gaps. (see missing data matrix)
2. In file "bland-altman-test.png" we can see that the 23-5 has 0 dB difference in actual vs 10 random values of all data in one sensor. There might be that there is not really much actual values and the 10 random values might be 90% of all values of those hours. (may be because the battery runs out and there is not much values in these times)
3. 4000*24 / 3600 = ca 27 (bland-altman actual vs 3635 has 0 db difference between actual median value and randomly picked 3635 values median value)
(3600 is wrong because one day has 1880 minutes, correct is 3635*24 / 1880 = ca 46 or 4000*24 / 1880 = ca 51)



## Task 6 
1. Find a treshold (110m)
2. Impute all the sensor in this circle
3. Switch main sensors imputation with the median value of all of these. (round median values up)
4. Do bland altman plot of one sensor imputation vs nearest sensor imputation
