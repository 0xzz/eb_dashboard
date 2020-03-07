###### Demand Estimation
* The green card demand and backlog are estimated based on 140 approval numbers and the multiplication factor. 
* Please note that these numbers do not equal to the amount of pending 485/CP applications. Instead, the numbers here equal to the "amount of green card demand who already has a PD".

###### 数据分析
* 请注意，这里的 **_140:GC_** 系数不是通常所说的家属系数，是指平均每份approve的140最终会带来多少张绿卡的需求. 
```py
通常情况下，140:GC = 家属系数 + 1 
```
* 具体到个人:
```py
如果你有1份140，最后一共申请2张绿卡，那么你个人的  140:GC = 2.0
如果你有2份140，最后只需要一张绿卡，那么你的  140:GC = 0.5
如果你有1份140, 最后选择了回国放弃绿卡, 那么你的  140:GC = 0
```
* 经过网友的测算，我们认为中国平均下来
```py
EB1的 140:GC 系数大约在2.0左右; 我们这里取了默认值2.0
EB23的 140:GC 系数大约在1.3-1.6之间, 并且由于NIW比例上升, 这个数字处于上升阶段；考虑到升降级机制，我们这里对EB2取了默认值1.4，EB3取了默认值1.0
```
* 如果您不认可这些数字，请输入您自己认为或者测算出来的数字，下面的demand和backlog图表会自动做出修正.