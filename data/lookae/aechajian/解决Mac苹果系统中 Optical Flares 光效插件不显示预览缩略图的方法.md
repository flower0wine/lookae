---
title: 解决Mac苹果系统中 Optical Flares 光效插件不显示预览缩略图的方法
slug: jie-jue-macping-guo-xi-tong-zhong-optical-flares-guang-xiao-cha-jian-bu-xian-shi-yu-lan-suo-lue-tu-de-fang-fa
source_url: https://www.lookae.com/optical-flares-preview/
category: aechajian
tags: [AE插件, Optical Flares]
---
# 解决Mac苹果系统中 Optical Flares 光效插件不显示预览缩略图的方法

2020/08/19 16:13

作者：大众脸
分类：[AE插件](https://www.lookae.com/after-effects/aechajian/) / [After Effects](https://www.lookae.com/after-effects/) / [Mac 专区](https://www.lookae.com/mac-osx/)

[AE插件](https://www.lookae.com/tag/ae%e6%8f%92%e4%bb%b6/)[Optical Flares](https://www.lookae.com/tag/optical-flares/)

很多朋友在Mac苹果系统上使用Optical Flares插件时，发现缩略图和预览不显示 (这种问题一般出现在10.15新系统中)。使用起来很费劲。如下图：

![解决Mac苹果系统中 Optical Flares 光效插件不显示预览缩略图的方法](https://img.alicdn.com/imgextra/i2/705956171/O1CN01CWRrn61vSMjswrmH7_!!705956171.jpg "解决Mac苹果系统中 Optical Flares 光效插件不显示预览缩略图的方法-LookAE.com")

导致该问题的具体原因我也不详，不过解决方法到是有的。(其实[VC官网](https://www.videocopilot.net/products/opticalflares/)已经更新了兼容10.15的插件版本，有能力请支持正版！)

**下面就来说一说，怎么临时解决这个不能预览的问题：**

打开“系统偏好设置 -> 显示器 -> 颜色”显示描述文件修改为“普通RGB描述文件”，这时候你会感觉显示器颜色已改变

![解决Mac苹果系统中 Optical Flares 光效插件不显示预览缩略图的方法](https://img.alicdn.com/imgextra/i4/705956171/O1CN01Xs7oXa1vSMjv4oeg0_!!705956171.jpg "解决Mac苹果系统中 Optical Flares 光效插件不显示预览缩略图的方法-LookAE.com")

然后回到AE（切换颜色描述文件不需要重启Ae），重新打开一下Optical Flares插件的独立面板。你就可以看到熟悉的预览界面了。

![解决Mac苹果系统中 Optical Flares 光效插件不显示预览缩略图的方法](https://img.alicdn.com/imgextra/i1/705956171/O1CN01XpaFtl1vSMjkEmXPA_!!705956171.jpg "解决Mac苹果系统中 Optical Flares 光效插件不显示预览缩略图的方法-LookAE.com")

其实灯光效果的显示，仅在Optical Flares的独立面板中不显示缩略图。当你回到Ae后，还是可以直接渲染出来的。并且切换Mac系统显示器的颜色描述文件时，不需要关闭Ae软件，只需要重新开一下Optical Falres的独立面板即可刷新。

Mac系统默认的颜色描述看起来还是不错的，我也是经常工作再默认的颜色模式下。所以当我把OF灯光在Option Flares独立面板里设置完成后，可以再接着设置回默认的颜色描述文件。看起来是个不错的解决方案。

【文章内容来自狐狸影视城，已征得站长同意转载和修改】

[镜头光晕耀斑AE插件 Optical Flares v1.3.5 Win/Mac 下载](https://www.lookae.com/optical-flares/)
