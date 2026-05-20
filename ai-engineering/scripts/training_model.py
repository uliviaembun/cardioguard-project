import tensorflow as tf
from tensorflow.keras import layers, Model
import pandas as pd
import numpy as np
import datetime
import os

# prepare path
current_dir = os.path.dirname(os.path.abspath(__file__))
base_ai_dir = os.path.join(current_dir, "..") # folder ai-engineering/

def get_path(folder, filename):
    return os.path.abspath(os.path.join(base_ai_dir, folder, filename))

# tambahkan .astype('float32') agar ramah bagi TensorFlow
X_train = pd.read_csv(get_path('data', 'X_train_scaled.csv')).values.astype('float32')
y_train = pd.read_csv(get_path('data', 'y_train.csv')).values.astype('float32')
X_test = pd.read_csv(get_path('data', 'X_test_scaled.csv')).values.astype('float32')
y_test = pd.read_csv(get_path('data', 'y_test.csv')).values.astype('float32')

# arsitektur model (Functional API)
def build_model(input_shape):
    inputs = layers.Input(shape=(input_shape,))
    x = layers.Dense(128, activation='relu')(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(64, activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.2)(x)
    x = layers.Dense(32, activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dense(16, activation='relu')(x)
    outputs = layers.Dense(1, activation='sigmoid')(x)
    return Model(inputs=inputs, outputs=outputs)

model = build_model(X_train.shape[1])

# setup Optimizer, Loss, dan Metrics
optimizer = tf.keras.optimizers.Adam(learning_rate=0.0005)
loss_fn = tf.keras.losses.BinaryCrossentropy()
train_acc_metric = tf.keras.metrics.BinaryAccuracy()
val_acc_metric = tf.keras.metrics.BinaryAccuracy()

# setup TensorBoard Logging
log_dir = "../logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
summary_writer = tf.summary.create_file_writer(log_dir)

# custom Training Step (tf.GradientTape)
@tf.function
def train_step(x, y):
    with tf.GradientTape() as tape:
        logits = model(x, training=True)
        loss_value = loss_fn(y, logits)
    
    grads = tape.gradient(loss_value, model.trainable_weights)
    optimizer.apply_gradients(zip(grads, model.trainable_weights))
    train_acc_metric.update_state(y, logits)
    return loss_value

# loop training manual dengan validasi dan logging ke TensorBoard
epochs = 50
batch_size = 32
train_dataset = tf.data.Dataset.from_tensor_slices((X_train, y_train)).batch(batch_size)

print(f"Mulai pelatihan untuk {epochs} epoch...")
for epoch in range(epochs):
    epoch_loss_avg = tf.keras.metrics.Mean()
    
    for step, (x_batch_train, y_batch_train) in enumerate(train_dataset):
        loss_value = train_step(x_batch_train, y_batch_train)
        epoch_loss_avg.update_state(loss_value)

    # Validasi di akhir setiap epoch
    val_logits = model(X_test, training=False)
    val_acc_metric.update_state(y_test, val_logits)
    
    # Log ke TensorBoard
    with summary_writer.as_default():
        tf.summary.scalar('loss', epoch_loss_avg.result(), step=epoch)
        tf.summary.scalar('accuracy', train_acc_metric.result(), step=epoch)
        tf.summary.scalar('val_accuracy', val_acc_metric.result(), step=epoch)

    if (epoch + 1) % 5 == 0:
        print(f"Epoch {epoch+1}: Loss: {epoch_loss_avg.result():.4f}, Acc: {train_acc_metric.result():.4f}, Val Acc: {val_acc_metric.result():.4f}")

    train_acc_metric.reset_state()
    val_acc_metric.reset_state()

# save model
save_path = get_path('models', 'cardioguard_model.keras')
model.save(save_path)
print(f"\nTraining selesai! Model disimpan di: {save_path}")
