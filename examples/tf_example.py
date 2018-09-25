import time
import tensorflow as tf


def handler(event):
    mnist = tf.keras.datasets.mnist

    (x_train, y_train),(x_test, y_test) = mnist.load_data()
    x_train, x_test = x_train / 255.0, x_test / 255.0

    model = tf.keras.models.Sequential([
      tf.keras.layers.Flatten(),
      tf.keras.layers.Dense(512, activation=tf.nn.relu),
      tf.keras.layers.Dropout(0.2),
      tf.keras.layers.Dense(10, activation=tf.nn.softmax)
    ])
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    print('Fitting!')
    history_callback = model.fit(x_train, y_train, epochs=5, callbacks=[])
    print(history_callback)
    print('Yeahhh')
    loss_history = history_callback.history["loss"]
    print(loss_history)

    model.evaluate(x_test, y_test)
