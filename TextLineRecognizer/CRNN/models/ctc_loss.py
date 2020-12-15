import tensorflow as tf

"""
CTC损失函数: tensorflow 2.3.1 官方文档
tf.nn.ctc_loss(labels, logits, label_length, logit_length, logits_time_major,blank_index)

labels: 真实标签,支持两种格式: 1.一维tensor,GPU/TPU训练时只能使用一维tensor, 2.稀疏tensor,推荐用于CPU训练,一维tensor也可用于CPU
        1:一维tensor, shape为[batch_size, max_label_seq_length],长度为数据集中的最大标签长度,标签长度不够时用0在尾部填充
            例如:有标签[2,5,3,7],[1,5],[2,8,9], 处理后为[ [2,5,3,7], [1,5,0,0], [2,8,9,0] ]
            注意: 在 GPU/TPU 上计算CTC时 !必须! 使用一维tensor, CPU上训练时也可使用一维tensor
            
        2:Sparse tensor稀疏张量, 例如:有标签[2,5,3,7],[1,5],[2,8,9], 处理后为: [indices, values, shape]
            indices=[(0,0),(0,1),(0,2),(0,3),(1,0),(1,1),(2,0),(2,1),(2,2)],
            values=[2,5,3,7,1,5,2,8,9],
            shape=(3,4), 3为行数,即标签的个数, 4为最大列数,即标签中的最大长度

logits: 网络预测值,有两种shape: 
        1:[frames, batch_size, num_labels] <--> [时序数, 批次大小, 类别数], logits_time_major为True时的shape
        
        2:[batch_size, frames, num_labels] <--> [批次大小, 时序数, 类别数], logits_time_major为False时的shape

label_length: 真实标签的长度序列,有两种格式: 
        1.一维tensor,shape为[batch_size],其值为真实标签的最大长度, 当labels为一维tensor时使用
        
        2.None, 当labels为Sparse tensor时使用
        
logit_length: 预测值的长度序列, shape为[batch_size], 其值为logits中的时序数/frames

logits_time_major: (可选),默认为True, 其值为True时 logits 的shape为[时序数, 批次大小, 类别数]
        其值为False时, shape为[批次大小, 时序数, 类别数]

blank_index: (可选),默认为0, ctc中预测的空格在词库中的下标, 负数则从后往前计算词库的下标
        例: 词库[a, 0, 1, b], blank_index为0时, 用a做ctc中的空格, blank_index为1时,用0做ctc中的空格, blank_index为正数时依此类推
        blank_index为-1时, 用b做ctc中的空格, blank_index为-2时, 用1做ctc中的空格, blank_index为负数时依此类推

Returns: ctc loss, 一维tensor, shape为[batch_size], 值为负对数概率(negative log probabilities).
"""


# 自定义CTC Loss函数
class CTCLoss(tf.keras.losses.Loss):
    def __init__(self, logits_time_major=False, blank_index=-1, 
                 reduction=tf.keras.losses.Reduction.AUTO, name='ctc_loss'):
        super().__init__(reduction=reduction, name=name)
        self.logits_time_major = logits_time_major      # 默认为False, 则logits/y_pred形状为 [批次大小, 时序数, 类别数]
        self.blank_index = blank_index                  # CTC中空格在词库中的位置, 默认值-1表示词库末尾

    def call(self, y_true, y_pred):
        y_true = tf.cast(y_true, tf.int32)              # 将 y_true 中的值转换成int类型
        # 默认y_pred形状为[批次大小, 时序数, 类别数], logit_length的形状为[batch_size], 其值为时序数
        logit_length = tf.fill([tf.shape(y_pred)[0]], tf.shape(y_pred)[1])  # 返回用时序数填充shape为[批次大小]的一维张量
        loss = tf.nn.ctc_loss(
            labels=y_true,                              # y_true为稀疏张量
            logits=y_pred,                              # 网络预测值, 默认shape为 [批次大小, 时序数, 类别数]
            label_length=None,                          # y_true为稀疏张量时, label_length设为None
            logit_length=logit_length,                  # 形状为[batch_size], 其值为时序数
            logits_time_major=self.logits_time_major,   # 默认为False
            blank_index=self.blank_index                # 默认为-1
            )
        return tf.reduce_mean(loss)


