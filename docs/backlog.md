#### Note
* Please note that the backlog here referes to the green card demands (regardless on if the petitioner has submitted 485 or not) that already have a PD. If a person already has an approved 140, we asume he/she brings or will bring _1*multiplication factor_ number of green card demands.

#### How Backlog Analysis will help you 如何理解backlog？
* The backlog analysis will help you understand how many people are in front of you in the long waiting queue. Based on simple computation, you can esitmate how long you would need to wait to get a green card.
* 如果你的pd是2018年2月1日, 那么可从下图中读出该pd对应的backlog数字. 这个数字是在你file 140的时候，pd在你之前的还没有绿的绿卡总需求.

#### How did we estimate the backlogs 我们是如何估算backlog的？
* The backlogs are estimated based on a simple demand-supply model plus an initial offset. The initial offset are estimated using historical visa bulletins.
* The green card demands are estimated based on the 140-GreeCard multiplication factors typed in the above 3x3 input grid
* Because EB2 PERM and EB3 PERM can relatively easily downgrade/upgrade, we have combined the backlog of EB2 and EB3 when plotting. 由于EB2和EB3 PERM之间可以比较容易的升降级, 历史上中国和row都大量存在这个情况, 在计算backlog的时候我们把eb23合并了.
* For EB1, we assume that at the end of FY 2013, all backlogs before 2013 and 40% of 2013 demand had been satisfied for all countries. 对于EB1, 我们假设在2013财年结束的时候，2013才年以前所有的demand均已被满足，并且2013财年自己产生的demand也已经有40%被满足. 这个假设是基于2013财年的时候全部国家都已经c了很长时间，并且前两年还存在无卡可发的情况.
* For China EB2 & EB3, we assume that at the end of FY2019, all backlogs before 2015 has been cleared and 80% of 2015 demands have been satisfied. This is because the VB for China-EB2 and 3 were at June and Nov 2015 at the end of FY2019. 对于中国EB23, 我们假设在2019财年结束的时候(2019年9月30日), 2015财年之前以及2015财年80%的EB23 demand已经被满足. 这是因为在19财年结束的时候中国EB2和EB3的排期分别为2015年6月和11月. 
* For Row EB2 & EB3, we assume that at the end of FY 2018, all backlogs before 2017 and 75% of 2017 demands had been satisfied. This is because the VBs for ROW EB2/3 were current at that time.
* For India EB2 & EB3, we assume that at the end of FY 2018, all backlogs before FY2009 and 50% of 2009 demands were cleared. This is because Inida EB2/3 moved to Mar 2009 and Jan 2009 at the end of FY 2019, respectively.
* We linearly extrapolate the backlog beyond 10/2019 assuming the same slope as last year. 针对2020财年开始的情况，我们对backlog做了线性外插值.
