import tensorflow as tf
from TextLineRecognizer.CRNN.models.config import NUM_CLASSES

# table: 词库list,
class Decoder:
    def __init__(self, table, blank_index=NUM_CLASSES-2, merge_repeated=True):
        """
        
        Args:
            table: list, char map
            blank_index: int(default: NUM_CLASSES - 1), the index of blank 
        label.
            merge_repeated: bool
        """
        self.table = table
        if blank_index == NUM_CLASSES-2:
            blank_index = len(table) - 1        # 默认为词库txt中的最后一个, 修改blank_index同时需要修改词库txt
        self.blank_index = blank_index
        self.merge_repeated = merge_repeated

    # 将转换后的数字标签解码成字符, inputs: [batch_size, time_steps] <--> [批次大小, 时序数]
    def map2string(self, inputs):
        strings = []        # 每个批次对应一个预测出的字符串
        for i in inputs:
            text = [self.table[char_index] for char_index in i 
                    if char_index != self.blank_index]      # TODO: 默认去除空格字符(转换成稠密矩阵时用空格字符进行填充), 预测空格需要用特殊符号做CTC中的空格, 然后将标签中的空格当作普通字符
            strings.append(''.join(text))
        return strings

    # 解码
    def decode(self, inputs, from_pred=True, method='greedy'):
        if from_pred:   # 对网络预测值解码
            logit_length = tf.fill([tf.shape(inputs)[0]], tf.shape(inputs)[1])  # 返回用时序数填充shape为[批次大小]的一维张量
            if method == 'greedy':  # ctc 贪心解码
                decoded, _ = tf.nn.ctc_greedy_decoder(
                    inputs=tf.transpose(inputs, perm=[1, 0, 2]),    # [批次大小, 时序数, 类别数] -> [时序数, 批次大小, 类别数]
                    sequence_length=logit_length,
                    merge_repeated=self.merge_repeated)
            elif method == 'beam_search':   # ctc beam search解码
                decoded, _ = tf.nn.ctc_beam_search_decoder(
                    inputs=tf.transpose(inputs, perm=[1, 0, 2]),    # [批次大小, 时序数, 类别数] -> [时序数, 批次大小, 类别数]
                    sequence_length=logit_length)
            inputs = decoded[0]     # 稀疏tensor
        decoded = tf.sparse.to_dense(inputs, 
                                     default_value=self.blank_index).numpy()
        decoded = self.map2string(decoded)
        return decoded