import tensorflow as tf

"""
CTC greedy decoder: tensorflow 2.3.1 官方文档
ctc_greedy_decoder(inputs, sequence_length, merge_repeated=True):

    inputs: 3维浮点型tensor, shape为[max_time, batch_size, num_classes] <--> [时序数, 批次大小, 类别数]
            即网络的预测输出值
    
    sequence_length: 1维int32类型的tensor, shape为[batch_size], 其值为时序数
    
    merge_repeated: 默认为True, 去除解码后的重复字符
  
    Returns: tuple (decoded, neg_sum_logits)
            
            decoded: 单一元素的列表, decoded[0]是其唯一的元素,decoded[0]是一个稀疏tensor,包含贪心解码后的结果
                     注: decoded[0]原形状为 [批次大小, 时序数]，其中的值为每个批次中当前时序所属的类别 
                     
                    `decoded.indices`: 下标矩阵, 
                    `decoded.values`: 一维向量, size为 [所有解码出的结果长度], 其值为对应的类别
                    `decoded.dense_shape`: Shape vector, size `(2)`.
    
            neg_sum_logits: A `float` matrix `(batch_size x 1)` containing, for the
                sequence found, the negative of the sum of the greatest logit at each
                timeframe.
"""

# 根据真实标签值来计算预测标签值的正确率
class WordAccuracy(tf.keras.metrics.Metric):
    def __init__(self, name='word_accuracy', **kwargs):
        super().__init__(name=name, **kwargs)
        self.total = self.add_weight(name='total', dtype=tf.int32, 
                                     initializer=tf.zeros_initializer())
        self.count = self.add_weight(name='count', dtype=tf.int32, 
                                     initializer=tf.zeros_initializer())

    # y_pred默认shape为[批次大小, 时序数, 类别数]
    # sparse_reset_shape: 重置稀疏tensor的形状,其下标和values不变,重置后的形状中每个维度都要大于等于原形状的中的每个维度
    def update_state(self, y_true, y_pred, sample_weight=None):
        b = tf.shape(y_true)[0]     # 取批次大小, 稀疏tensor的shape为[batch_size, 最大标签长度]
        max_width = tf.maximum(tf.shape(y_true)[1], tf.shape(y_pred)[1])     # TODO: 取真实标签的最大长度 与 时序数 中的最大值
        logit_length = tf.fill([tf.shape(y_pred)[0]], tf.shape(y_pred)[1])   # 返回用时序数填充shape为[批次大小]的一维张量
        decoded, _ = tf.nn.ctc_greedy_decoder(                  # ctc 贪心解码网络预测值
            inputs=tf.transpose(y_pred, perm=[1, 0, 2]),        # [批次大小, 时序数, 类别数] -> [时序数, 批次大小, 类别数]
            sequence_length=logit_length)
        y_true = tf.sparse.reset_shape(y_true, [b, max_width])      # 重置稀疏tensor的形状, [批次大小, 最大宽度]
        y_pred = tf.sparse.reset_shape(decoded[0], [b, max_width])  # 重置稀疏tensor的形状, [批次大小, 最大宽度]
        y_true = tf.sparse.to_dense(y_true, default_value=-1)       # y_true稀疏矩阵转成稠密矩阵, 缺失值用-1填充
        y_pred = tf.sparse.to_dense(y_pred, default_value=-1)       # y_pred稀疏矩阵转成稠密矩阵, 缺失值用-1填充
        y_true = tf.cast(y_true, tf.int32)                          # y_true和y_pred转成稠密矩阵后, 其值可以一一对应
        y_pred = tf.cast(y_pred, tf.int32)
        values = tf.math.reduce_any(tf.math.not_equal(y_true, y_pred), axis=1)  # 统计y_true和y_pred不同的值的个数
        values = tf.cast(values, tf.int32)                          # values为一维tensor, shape为[batch_size]
        values = tf.reduce_sum(values)                              # 统计values中不同(1)的个数
        self.total.assign_add(b)                                    # 总数为批次大小
        self.count.assign_add(b - values)                           # 相同的个数

    def result(self):
        return self.count / self.total

    def reset_states(self):
        self.count.assign(0)
        self.total.assign(0)