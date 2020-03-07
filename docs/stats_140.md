###### Data source:
* Data source from USCIS Immigration Data [Here](https://www.uscis.gov/sites/default/files/USCIS/Resources/Reports%20and%20Studies/Immigration%20Forms%20Data/Employment-based/I140_by_class_country_FY09_19.pdf)
* Please note that the approved numbers of FY2019 have been adjusted using the pending numbers and FY2019 denial rate. The safe EB 140 thresholds are computed using 40k divided by the corresponding global EB1,2,3 multiplication factors: 2.4, 2.0, and 2.1, respectively.

###### 数据来源:
* 移民局公布数据 [链接](https://www.uscis.gov/sites/default/files/USCIS/Resources/Reports%20and%20Studies/Immigration%20Forms%20Data/Employment-based/I140_by_class_country_FY09_19.pdf)
* 其中FY2019的数据有调整：根据FY2019已经处理的数据估算批准率，然后推算总批准数
* 图表中默认包含的数据类别有：中国/ROW/印度的EB1/EB2/EB3的140数量。单击图表右侧的数据类别，可以选择在图表上添加/移除该类数据。可以在图表中选择感兴趣的数据进行比较；可以切换Group和Stack图类型；

###### 140历史数据详细分析:
* 图中的“140安全线”是通过现有的全球EB绿卡限额上限（40040）除以“转换系数”估算得到
* “转换系数”的定义：**1** 份批准的140申请在最终会转换为 **X** 张绿卡，系数即为 **X**; 这里“转换系数”包含了各种需要估算的效应最后在系数上的结果；主要包括：最终提交申请时的配偶子女数，跳槽有多份申请，EB2/3升降级，EB1/NIW升降级，等等。
* 其中配偶子女数量部分的估算，可参考移民局[文件数据](https://www.uscis.gov/sites/default/files/files/nativedocuments/Count_of_Approved_I-140_I-360_and_I-526_Petitions_as_of_April_20_2018_with_a_Priority_Date_On_or_After_May_2018.PDF)（针对全球申请人）
```py
Cat: Muliplication Factor
EB1: 1 + 1.4 = 2.4  
EB2: 1 + 1.0 = 2.0  
EB3: 1 + 1.1 = 2.1
```


