---
title: 接触
date: '2024-07-12 14:35:15'
updated: '2024-07-12 14:52:58'
permalink: /post/touch-gxoly.html
comments: true
toc: true
---

# 接触

# 类型

**Bonded（绑定）** ：

* 默认接触形式，不允许界面或单元相对滑动或分离，即使加载或移除载荷后也能保持接触。
* 法线方向 **不可分开** ，切向也不行

**No Separation（不分离）** ：

* 不允许分离，即使加载或移除载荷后，界面不允许接触面分离，但允许相对滑动。相当于相对面间有小范围滑动，即法向不可分离，切向可以有小位移。
* 法线方向 **不可分开** ，切线方向可以发生轻微的相对滑动。

**Frictionless（无摩擦）** ：

* 允许分离，允许产生相对滑动，界面出现分离时则法向压力为零，同时假设接触面无摩擦。
* 法线方向 **可以分开** ，切线方向 **可以发生相对滑动** ， **且没有摩擦力** 。

**Rough（粗糙）** ：

* 允许分离，但不允许摩擦。允许界面完全的摩擦接触，即没有相对滑动，法向可分离，切向不可滑动。
* 法线方向 **可以分开** ，切线方向 **不可以** 发生相对滑动。

**Frictional（有摩擦）** ：

* 允许分离，允许产生相对滑动，两接触面间有摩擦力。法向可分离，切向摩擦滑动。
* 法线方向 **可以分开** ，切线方向 **可以** 发生相对滑动， **有摩擦力。** 
