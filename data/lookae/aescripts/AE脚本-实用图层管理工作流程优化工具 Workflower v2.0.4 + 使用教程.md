---
title: AE脚本-实用图层管理工作流程优化工具 Workflower v2.0.4 + 使用教程
slug: aejiao-ben-shi-yong-tu-ceng-guan-li-gong-zuo-liu-cheng-you-hua-gong-ju-workflower-v2-0-4-shi-yong-jiao-cheng
source_url: https://www.lookae.com/workflower-202/
category: aescripts
tags: [AE脚本, Workflower]
---
# AE脚本-实用图层管理工作流程优化工具 Workflower v2.0.4 + 使用教程

2024/01/17 19:28

作者：大众脸
分类：[AE脚本](https://www.lookae.com/after-effects/aescripts/) / [After Effects](https://www.lookae.com/after-effects/)

[AE脚本](https://www.lookae.com/tag/ae%e8%84%9a%e6%9c%ac/)[Workflower](https://www.lookae.com/tag/workflower/)

![AE脚本-实用图层管理工作流程优化工具 Workflower v2.0.4 + 使用教程](https://www.lookae.com/wp-content/uploads/2023/05/Workflower-v2.jpg "AE脚本-实用图层管理工作流程优化工具 Workflower v2.0.4 + 使用教程-LookAE.com")

[﻿﻿﻿](https://cloud.video.taobao.com//play/u/705956171/p/1/e/6/t/1/409642796376.mp4)

对凌乱的After Effects图层/合成感到恼火？使用Workflower脚本，您可以在合成中创建图层组，以及使用其他工作流程增强工具，例如将对图层合成进行分组、塌陷、选择移动、复制连接、仅选定图层、图层克隆、遮罩合并、添加标签等多种操作。

Annoyed by messy After Effects comps? With Workflower, you can create layer groups within your comp, as well as use other workflow-enhancing tools, like adjustment layers to selected layers only, layer cloning, or matte merging.

**v2.0.4更新内容：**

[添加]  
– 与 AE 24.1 中引入的新“高级 3D”渲染器完全兼容。  
– “按编号重命名图层”现在允许您定义要重新编号的增量以及保留特定后缀。为此，请转到“设置 > 命名 > 执行按编号重命名图层时：”。  
– “按数字重命名图层”现在也适用于项目面板项目。确保当前合成中没有选择任何图层，然后选择项目面板项并执行“按编号重命名图层”。重要提示：只有当您从菜单（而不是通过快捷方式）执行该功能时，这才有效。  
– 您现在可以通过选择项目面板项目并执行“复制图层/克隆/组”来复制项目面板项目。当您复制合成时，它将打开复制合成的时间线并使其所有“预合成克隆”独立。重要提示：只有当您从菜单（而不是通过快捷方式）执行该功能并且您当前活动的合成中没有选择任何图层（否则 Workflower 将复制选定的图层）时，此功能才有效！  
– 当“预合成克隆”位于选择范围内时执行“粘贴存储的图层”时，Workflower 现在将创建独特的“预合成克隆”，并可能将包含的“从属克隆”更新为新的克隆合成。  
– 项目面板中的“克隆”和“存储图层”文件夹现在将仅通过其名称而不是其项目注释进行标识。这使得 Workflower 与依赖文件夹项目注释的附加组件（如“Pro IO”）兼容。  
– [Beta 功能]：现在可以添加图层注释，而无需 Workflower 覆盖它们。这也使得 Workflower 与依赖于向图层注释写入数据/从图层注释读取数据的各种附加组件兼容（例如“Flatten Layers”或“AutoSway”）。Workflower 通过在添加非 Workflower 图层注释时将其数据保存到图层标记来实现此目的。不要删除该标记！使用非 Workflower 图层注释会降低 Workflower 函数的性能，因此建议尽可能少使用。要使用图层注释返回 Workflower 来存储数据，只需将空字符串放入图层注释中并执行任何 Workflower 函数即可。由于此功能仍处于测试阶段，您必须在“设置 > 布局 > 允许外部层注释”下启用它。  
– 当右键单击主菜单上的某些功能（如抠图、克隆或命名功能）时，您现在可以直接访问专用设置页面。  
– 现在，您可以通过右键单击 ScriptUI 面板上的空白区域并选择“导出/导入项目”来快速访问“将所有组合转换为另一个布局”功能。

– 当您执行需要活动组件但没有活动组件的函数时，您现在会收到错误消息。  
– 向脚本 API 添加了函数“wfAPI.refeshLayouts(comps[, doNotLabelLayersOutsideToNone])”。这允许您一次刷新多个组合的布局，从而使整体执行速度更快。  
– 在脚本 API 中添加了函数“wfAPI.isInTagID(layer, tagID)”和“wfAPI.isInTagName(layer, tagName)”。这将检查给定图层是否位于具有特定 ID (0 – 16) 或名称的标签组内。

[更改]  
– 当“刷新布局”或“按数字重命名图层”重新编号图层名称时，当最后一个字符为“0”或“0”等符号时，Workflower 现在不会在原始名称和新数字之间添加空格\_’。  
– 当您执行“按数字重命名图层”时，Workflower 现在将在整个重命名过程发生\*之后\*尝试为每个选定的名称找到唯一的名称。

[已修复]  
– 修复了执行“显示图层不透明度”时的错误，该错误会错误地显示图层上的其他属性。  
– 修复了显示/隐藏“Prime Clone”图层和隐藏图层效果属性时发生的错误（例如，在“Element 3D”等的某些情况下）。  
– 修复了“预合成克隆”及时移动且其关键帧变为负数后“刷新布局”期间可能发生的错误。

支持Win/Mac系统：AE 2024, 2023, 2022, 2021, 2020, CC 2019, CC 2018

**【下载地址】**

脚本： [城通网盘](https://url70.ctfile.com/f/2827370-1009077686-cce5f2?p=4431) 访问密码：6688       [百度网盘](https://pan.baidu.com/s/1jQxeyArUth-3DxM4VNEyVA?pwd=nn2q) 提取码：nn2q           [阿里云盘](https://www.alipan.com/s/cP3nZmnZH39)

教程： [城通网盘](https://url70.ctfile.com/f/2827370-857577171-ff7593?p=4431) 访问密码：6688       [百度网盘](https://pan.baidu.com/s/1DlU8yu92raTeIwD7K-rYpg?pwd=oc4t) 提取码：oc4t           [阿里云盘](https://www.aliyundrive.com/s/AFAgodJPNEc)
