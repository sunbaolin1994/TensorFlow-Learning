import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

batchsz = 128
total_words = 10000
max_review_len = 80
embedding_len = 100


(x_train, y_train), (x_test, y_test) = keras.datasets.imdb.load_data(num_words = total_words)
x_train = keras.preprocessing.sequence.pad_sequences(x_train, maxlen = max_review_len)
x_test = keras.preprocessing.sequence.pad_sequences(x_test, maxlen = max_review_len)

db_train = tf.data.Dataset.from_tensor_slices((x_train, y_train))
db_train = db_train.shuffle(1000).batch(batchsz, drop_remainder = True)
db_test = tf.data.Dataset.from_tensor_slices((x_test, y_test))
db_test = db_test.batch(batchsz, drop_remainder = True)

class MyRNN(keras.Model):
    
    def __init__(self, units):
        super(MyRNN, self).__init__()

        # transform text to embedding representation
        # [b, 80] => [b, 80, 100]
        self.embedding = layers.Embedding(total_words, embedding_len, input_length = max_review_len)

        # simple rnn
        self.rnn = keras.Sequential([
            layers.GRU(units, dropout = 0.5, return_sequences = True, unroll = True),
            layers.GRU(units, dropout = 0.5, unroll = True)
        ])

        # fc, [b, 80, 100] => [b, 64] => [b, 1]
        self.outlayer = layers.Dense(1)

    def call(self, inputs, training = None):
        
        # [b, 80]
        x = inputs

        # embedding: [b, 80] => [b, 80, 100]
        x = self.embedding(x)

        # rnn cell compute
        # [b, 80, 100] => [b, 64]
        x = self.rnn(x, training = training)

        # out: [b, 64] => [b, 1]
        x = self.outlayer(x)

        prob = tf.sigmoid(x)

        return prob


def main():
    units = 64
    epochs = 4

    model = MyRNN(units)
    model.compile(optimizer = keras.optimizers.Adam(0.001),
                    loss = tf.losses.BinaryCrossentropy(),
                    metrics = ['accuracy'])
    model.fit(db_train, epochs = epochs, validation_data = db_test)

    model.evaluate(db_test)



if __name__ == "__main__":
    main()