###### How might backlog analysis help you?
* The backlog analysis helps you better understand your place in the green card backlog queue, i.e. how many people are in front of you. This enables you to better estimate how long you would need to wait to get a green card.
* Please note that the backlog here refers to the cumulative number of prospective green card beneficiaries. Colloquially we also refer to this as the *green card demand*. This demand is irrespective of whether the petitioner has submitted 485 or not. If a person has been granted I-140 approval, we assume he/she will bring _1*multiplication factor_ number of green card demands.
* The aforementioned multiplication factor is a holistic fudge factor to account for green cards requested for dependents, duplicated filing because of job change, ineligibility due to permanent job loss etc.

###### How do we estimate the backlog? 
* Because EB2 and EB3 PERM can relatively easily downgrade/upgrade, we have combined the backlog of EB2 and EB3 when plotting. 
* The green card demands are estimated based on the 140-GreenCard multiplication factor as provided in the 3x3 input grid above.
* The backlogs are estimated based on a simple demand-supply model plus an initial offset. The initial offset are estimated using historical visa bulletins.
```markdown
For EB1, we assume that at the end of FY2013, all backlogs before FY2013 and 40% of FY2013 demand had been satisfied for all countries. 

For China EB2, we assume that at the end of FY2019, all backlogs before 2015 had been cleared and 75% of 2015 demands had been satisfied. 
For China EB3, we assume that at the end of FY2019, all backlogs before 2016 had been cleared. 
[At the end of FY2019, VB for China-EB2 @ June 2015 and China-EB3 @ Nov 2015 (estimated "real" value based on Oct 2019(FY2020) VB)] 

For India EB2 & EB3, we assume that at the end of FY2018, all backlogs before FY2009 and 50% of 2009 demands had been cleared. 
[At the end of FY2019, VB for Inida EB2 @ Mar 2009 and India-EB3 @ Jan 2009 respectively]

For Rest-of-the-World (ROW) EB2 & EB3, we assume that at the end of FY 2018, all backlogs before 2017 and 75% of 2017 demands had been satisfied. 
[VB for ROW EB2/3 were current at that time]
```
* We linearly extrapolate the backlogs beyond 10/2019 assuming the same slope as the last year. 



###### 如何理解backlog？
* 如果你的PD是2018年2月1日, 那么可从下图中读出该pd对应的backlog数字. 这个数字是在你file 140的时候，PD在你之前的还没有绿的绿卡总需求.

###### 我们是如何估算backlog的？
* 由于EB2和EB3 PERM之间可以比较容易的升降级, 历史上中国和ROW都大量存在这个情况, 在计算backlog的时候我们把EB23合并了.
* 对于EB1, 我们假设在2013财年结束的时候，2013财年以前所有的demand均已被满足，并且2013财年自己产生的demand也已经有40%被满足. 这个假设是基于2013财年的时候全部国家都已经c了很长时间，并且前两年还存在无卡可发的情况.
* 对于中国EB2, 我们假设在2019财年结束的时候, 2015财年之前以及2015财年75%的EB2 demand已经被满足. 对于中国EB3, 我们假设在2019财年结束的时候, 2016财年之前的EB3 demand已经被满足. 这是因为在19财年结束的时候中国EB2和EB3的排期分别约为2015年6月和11月（根据20财年开年数据估算得到的“真实”排期）. 
* 针对2020财年开始的情况，我们对backlog做了线性外插值.