# Graph-Edit-Distance

## Introduction

Graph Edit Distance is an error-tolerant matching-based method that can be used to compute a dissimilarity
measure between two graphs.

Since it's such an important problem, many methods have been proposed to solve it.

I try to solve this problem in the following sequence:
- A* Search
- Hausdorff Distance
- Linear Programming

I will introduce our specfic work in the following part.

## Different methods

### A* Search

A* Search is probable the earliest and the most simple way that people will try to use when considering about the problem, but it's limited due to the exponential increase cost of the memory and time.

Improvements do exist.

For examples
- Algorithms for computing lower bound and upper bound of the future cost in a search tree have been come into use just like Munkres’ algorithm.
- Vertices-Sorting strategy has been proposed to search nodes which are more possible to get the best result prior.
- More efficient reduction strategy makes it possible for the memory consumption to be not so exhausted.

However, I gave up this method after some attempts because it's difficult to write code for the improved A* Search part and its time can't meet our demand.(30 seconds for one graph)

### Hausdorff Distance

Due to the time limitation, for comparison between graphs which contains more than 20 nodes, it's hard to compute the exact Graph Edit Distance in 30 seconds. We need some aproximate methods which can give an acceptable result, Hausdorff Distance is one of them.

Let's briefly introduce the Hausdorff Distance. It can compute the distance of the nearest neighbors between two sets and as a result, it's a new way to define graph distance. Luckily, the way how Hausdorff Distance works is quite similar to GED, and a paper says that  the experiment results show that the HED can reach the level about 90% accuracy when comparing to GED. The most important thing is that HED can be computed in only O(n1 * n2) time where n1 and n2 represent the node nums of two graphs. That is to say, we can easily use this method to approximate almost GED computation process.

### Linear Programming

It's clear that the GED problem can be seen as an ILP problem as well. We just simply use some binary varibles to represent how we change the map and add some constraints to the modle. The cost is determined by our parameter setting. And the problem is now becoming how to solve a 0-1 linear programming which is a NP-HARD problem. Fortunately, we have some packages which can help us to solve the problem for simple cases which is enough for most graphs in the data sets. Don't forget to optimize your linear model, it can help improve the speed and quality of solving process a lot.

### Summary

OK, it's time to have a review of what we have done to solve the GED problem.

We started from trying the basic A* search method but failed. Then we could successfully compute the approximate GED by using the Hausdorff Distance. But we were not satisified with the approximate solution and we finally use the linear programming to compute the exact Graph Edit Distance for most graphs.

Finally what we want to say is that GED is actually a real world problem, people pay lots attention to it and try to balance between speed and quality(usually with high costs). It's such an interesting problem that new methods are still been proposed after so many years, We'd like to pay continuous attention to the GED and learn the newest methods for solving it!

### References

These are papers which help us most when solving this problem.
- Approximation of graph edit distance based on Hausdorff matching
- Graph edit distance : a new binary linear
programming formulation
- An Exact Graph Edit Distance Algorithm for Solving
Pattern Recognition Problems
