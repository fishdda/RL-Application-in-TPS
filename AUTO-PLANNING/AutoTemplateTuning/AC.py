import tensorflow as tf
import numpy as np

LR_A = 0.0001
LR_C = 0.0001
ENTROPY_BETA = 0
GAMMA = 0.9
EPOCH = 200
ALPHA = 1.0

N_Sinf = 18*4          # an integer, number of cost functions * 4 (for IE, IC, WGT, RLP)
N_Sdvh = 11            # an integer, number of prescription functions
N_A = 18               # an integer, number of cost functions
A_BOUND = np.tile([0,1.0],(N_A,1)).transpose().reshape((2,N_A))     # a list of [lower bound, upper bound]
                    # lower bound and upper bound are arrays of size N_A
                    # provides a bound for the actions which consists of values to be added to IC


class ACNet(object):
    def __init__(self, scope, sess):

        self.sess = sess
        self.actor_optimizer = tf.train.AdamOptimizer(LR_A, name='AdamA')
        self.critic_optimizer = tf.train.AdamOptimizer(LR_C, name='AdamC')

        with tf.variable_scope(scope):
            self.s_inf = tf.placeholder(tf.float32, [None, N_Sinf], 'Sinf')
            self.s_dvh = tf.placeholder(tf.float32, [None, N_Sdvh], 'Sdvh')
            self.a_his = tf.placeholder(tf.float32, [None, N_A], 'A')
            self.v_target = tf.placeholder(tf.float32, [None, 1], 'Vtarget')

            mu, sigma, self.v, self.a_params, self.c_params = self._build_net(scope)

            td = tf.subtract(self.v_target, self.v, name='TD_error')
            
            with tf.name_scope('c_loss'):
                self.c_loss = tf.reduce_mean(tf.square(td))

            with tf.name_scope('wrap_a_out'):
                mu, sigma = mu * A_BOUND[1], sigma + 1e-4

            normal_dist = tf.contrib.distributions.Normal(mu, sigma)

            with tf.name_scope('a_loss'):
                log_prob = normal_dist.log_prob(self.a_his)
                exp_v = log_prob * td
                entropy = normal_dist.entropy()
                self.exp_v = ENTROPY_BETA * entropy + exp_v
                self.a_loss = tf.reduce_mean(-self.exp_v)

            with tf.name_scope('choose_a'):
                self.A = tf.clip_by_value(tf.squeeze(normal_dist.sample(1), axis=0), A_BOUND[0], A_BOUND[1])

            with tf.name_scope('optimizer'):
                self.update_a_op = self.actor_optimizer.minimize(self.a_loss, var_list=self.a_params)
                self.update_c_op = self.critic_optimizer.minimize(self.c_loss, var_list=self.c_params)
    
    def _build_net(self, scope):
        with tf.variable_scope('actor'):
            dense0_inf = tf.layers.dense(self.s_inf, 128, tf.nn.relu6, name='dense0_inf')
            dense0_dvh = tf.layers.dense(self.s_dvh, 32, tf.nn.relu6, name='dense0_dvh')

            concat = tf.concat([dense0_inf, dense0_dvh], axis=1)
            dense0 = tf.layers.dense(concat, 256, tf.nn.relu6, name='dense0')
            dense1 = tf.layers.dense(dense0, 64, tf.nn.relu6, name='dense1')

            mu = tf.layers.dense(dense1, N_A, tf.nn.tanh, name='mu')
            sigma = tf.layers.dense(dense1, N_A, tf.nn.softplus, name='sigma')
        
        with tf.variable_scope('critic'):
            dense0_inf = tf.layers.dense(self.s_inf, 128, tf.nn.relu6, name='dense0_inf')
            dense0_dvh = tf.layers.dense(self.s_dvh, 32, tf.nn.relu6, name='dense0_dvh')

            concat = tf.concat([dense0_inf, dense0_dvh], axis=1)
            dense0 = tf.layers.dense(concat, 256, tf.nn.relu6, name='dense0')
            dense1 = tf.layers.dense(dense0, 64, tf.nn.relu6, name='dense1')
            v = tf.layers.dense(dense1, 1, name='v')

        a_params = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=scope+'/actor')
        c_params = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=scope+'/critic')

        return mu, sigma, v, a_params, c_params

    def update(self, feed_dict):
        self.sess.run([self.update_a_op, self.update_c_op], feed_dict)

    def choose_action(self, s_inf, s_dvh):
        s_inf = s_inf[np.newaxis, :]
        s_dvh = s_dvh[np.newaxis, :]
        return self.sess.run(self.A, {self.s_inf:s_inf, self.s_dvh:s_dvh})[0]

class Worker(object):
    def __init__(self, name, sess):
        self.name = name
        self.sess = sess
        self.AC = ACNet(name, sess)
        self.R = 0

        self.buffer_s_inf = []
        self.buffer_s_dvh = []
        self.buffer_s_inf_ = []
        self.buffer_s_dvh_ = []
        self.buffer_a = []
        self.buffer_r = []

    def predict(self, state_inf, state_dvh):
        return self.AC.choose_action(state_inf, state_dvh)

    def update(self, state1_inf, state1_dvh, state2_inf, state2_dvh, action, reward, update=False):
        self.buffer_s_inf.append(state1_inf)
        self.buffer_s_dvh.append(state1_dvh)
        self.buffer_s_inf_.append(state2_inf)
        self.buffer_s_dvh_.append(state2_dvh)
        self.buffer_a.append(action)
        self.buffer_r.append(reward)

        self.R = self.R + ALPHA * (reward-self.R)

        if update:
            self.buffer_r = self.buffer_r - self.R
            v_s = self.sess.run(self.AC.v, {self.AC.s_inf: np.vstack(self.buffer_s_inf),
                                            self.AC.s_dvh: np.vstack(self.buffer_s_dvh)})
            buffer_v_target = [r + GAMMA * v for (v,r) in zip(v_s, self.buffer_r)]

            feed_dict = {self.AC.s_inf: np.vstack(self.buffer_s_inf),
                         self.AC.s_dvh: np.vstack(self.buffer_s_dvh),
                         self.AC.a_his: np.vstack(self.buffer_a),
                         self.AC.v_target: np.vstack(buffer_v_target)}

            self.AC.update(feed_dict)

            self.buffer_s_inf = []
            self.buffer_s_dvh = []
            self.buffer_s_inf_ = []
            self.buffer_s_dvh_ = []
            self.buffer_a = []
            self.buffer_r = []
