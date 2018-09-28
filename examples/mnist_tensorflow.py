import tensorflow as tf


def handler(event):
    tf.logging.set_verbosity(tf.logging.INFO)
    p1 = int(event[0])
    p2 = float(event[1])
    p3 = int(event[2])
    p4 = int(event[3])
    mnist = tf.keras.datasets.mnist

    (x_train, y_train),(x_test, y_test) = mnist.load_data()
    x_train, x_test = x_train / 255.0, x_test / 255.0

    model = tf.keras.models.Sequential([
      tf.keras.layers.Flatten(),
      tf.keras.layers.Dense(p1, activation=tf.nn.relu),
      tf.keras.layers.Dropout(p2),
      tf.keras.layers.Dense(p3, activation=tf.nn.softmax)
    ])
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    tf.logging.info(model.fit(x_train, y_train, epochs=p4))
    e = model.evaluate(x_test, y_test)
    tf.logging.info(e)
    return e[-1]
