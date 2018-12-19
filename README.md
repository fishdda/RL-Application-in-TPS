# RL-Application-in-TPS
**Utilizing Reinforcement Learning to make an auto-planning treatment planning system**

- This project is intended to make a new toolbox to optimize a rule-based model auto-planning platform on Monaco TPS.
- To build up a new plan evaluation system for physician as a reference.
- First to use genetic algorithm to replace the current template modifier.
![alt text](https://github.com/fishdda/RL-Application-in-TPS/blob/master/fig20.png)


**Based on the current bio-optimization, a function(f) would be developed for updating template.**
- <img src="https://latex.codecogs.com/gif.latex?x_{i&plus;1}&space;=&space;x_{i}&space;&plus;&space;\delta_{i}*\lambda_{i}" title="x_{i+1} = x_{i} + \delta_{i}*\lambda_{i}" />

- <img src="https://latex.codecogs.com/gif.latex?\delta_{i}&space;=&space;f_{i}(x_{i},y_{i},z_{i},m_{i},n_{i})&space;;&space;\lambda_{i}&space;=&space;\left\{\begin{matrix}&space;1&if&space;Q_{i}\leq0.5&space;\\&space;-1&if&space;Q_{i}&space;>&space;0.5&space;\end{matrix}\right." title="\delta_{i} = f_{i}(x_{i},y_{i},z_{i},m_{i},n_{i}) ; \lambda_{i} = \left\{\begin{matrix} 1&if Q_{i}\leq0.5 \\ -1&if Q_{i} > 0.5 \end{matrix}\right." />

- <img src="https://latex.codecogs.com/gif.latex?x_{i}=&space;$isoconstraint_{i}$;&space;y_{i}&space;=&space;$isoeffect_{i}$;&space;z_{i}&space;=&space;$weight_{i}$;&space;m_{i}&space;=&space;$relative\&space;impact_{i}$;&space;\\&space;\indent&space;n_{i}&space;=&space;$DVH_{i}$;&space;Q{i}&space;=&space;$possibility\&space;of\&space;direction_{i}$." title="x_{i}= $isoconstraint_{i}$; y_{i} = $isoeffect_{i}$; z_{i} = $weight_{i}$; m_{i} = $relative\ impact_{i}$; \\ \indent n_{i} = $DVH_{i}$; Q{i} = $possibility\ of\ direction_{i}$." />

**Currently, f is a rule-based function with the prior knowledge or experience of planners.**


**In future, f should be optimized to be more intelligent with evolution algorithm or reinforcement learning.**
