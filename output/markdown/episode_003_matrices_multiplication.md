# Episode 3: Matrices and Multiplication

## Yesterday's Recap

In Episode 2, we explored the fundamental concept of **dot products and projections**. Here are the key takeaways:

- **Dot Product**: We learned that the dot product $\mathbf{a} \cdot \mathbf{b} = \sum_{i=1}^{n} a_i b_i$ measures how much two vectors point in the same direction
- **Geometric Interpretation**: $\mathbf{a} \cdot \mathbf{b} = |\mathbf{a}||\mathbf{b}|\cos\theta$, where $\theta$ is the angle between vectors
- **Projections**: We discovered how to project one vector onto another using $\text{proj}_{\mathbf{b}}\mathbf{a} = \frac{\mathbf{a} \cdot \mathbf{b}}{|\mathbf{b}|^2}\mathbf{b}$
- **Applications**: We saw how dot products power similarity measures in recommendation systems and are fundamental to neural network operations

These concepts form the foundation for today's topic: matrices and matrix multiplication. While dot products work with one-dimensional arrays (vectors), matrices extend these ideas to two-dimensional arrays, enabling us to perform multiple operations simultaneously and represent complex transformations.

## Today's Topic: Matrices and Multiplication

Imagine you're building a neural network to classify images. Each layer needs to transform hundreds or thousands of input values into output values through weighted connections. How do you efficiently represent and compute all these transformations? The answer is **matrices**.

A matrix is fundamentally a rectangular array of numbers, but in AI/ML, it's so much more. It's a way to:
- Represent datasets (each row is a sample, each column is a feature)
- Encode transformations (rotation, scaling, projection)
- Store neural network weights
- Perform batch operations on multiple vectors simultaneously

Today, we'll master the mechanics of matrices and their multiplication — arguably the most important operation in all of machine learning. By the end of this episode, you'll understand why GPUs are optimized for matrix operations and how a simple multiplication can encode complex transformations.

### Why Matrix Multiplication Matters in AI/ML

Consider a simple neural network layer with 3 inputs and 2 outputs. Each output is a weighted combination of all inputs:

```
output1 = w11*input1 + w12*input2 + w13*input3 + b1
output2 = w21*input1 + w22*input2 + w23*input3 + b2
```

With matrix multiplication, we can write this compactly as:

$$\begin{bmatrix} \text{output}_1 \\ \text{output}_2 \end{bmatrix} = \begin{bmatrix} w_{11} & w_{12} & w_{13} \\ w_{21} & w_{22} & w_{23} \end{bmatrix} \begin{bmatrix} \text{input}_1 \\ \text{input}_2 \\ \text{input}_3 \end{bmatrix} + \begin{bmatrix} b_1 \\ b_2 \end{bmatrix}$$

This is just the beginning. Matrix multiplication enables:
- **Batch processing**: Process multiple samples simultaneously
- **Chain transformations**: Compose multiple operations
- **Efficient computation**: Leverage optimized libraries and GPU acceleration
- **Theoretical analysis**: Use linear algebra properties to understand model behavior

## Core Concepts

### What is a Matrix?

**Intuition**: Think of a matrix as a spreadsheet or table of numbers. Each number has a specific position identified by its row and column.

**Formal Definition**: A matrix $A$ is a rectangular array of elements arranged in $m$ rows and $n$ columns:

$$A = \begin{bmatrix}
a_{11} & a_{12} & \cdots & a_{1n} \\
a_{21} & a_{22} & \cdots & a_{2n} \\
\vdots & \vdots & \ddots & \vdots \\
a_{m1} & a_{m2} & \cdots & a_{mn}
\end{bmatrix}$$

Where:
- $m$ = number of rows
- $n$ = number of columns  
- $a_{ij}$ = element in row $i$, column $j$
- We say $A$ is an $m \times n$ matrix (read as "m by n")

```python
import numpy as np
import matplotlib.pyplot as plt

# Creating matrices in Python
# Method 1: From nested lists
A = np.array([
    [1, 2, 3],    # First row
    [4, 5, 6]     # Second row
])
print("Matrix A (2×3):")
print(A)
print(f"Shape: {A.shape}")  # (rows, columns)

# Method 2: Using NumPy functions
B = np.zeros((3, 4))        # 3×4 matrix of zeros
C = np.ones((2, 2))         # 2×2 matrix of ones  
D = np.eye(3)               # 3×3 identity matrix
E = np.random.randn(2, 3)   # 2×3 matrix with random values

# Accessing elements
print(f"\nElement at row 1, column 2 of A: {A[0, 1]}")  # Remember: 0-indexed!
print(f"First row of A: {A[0, :]}")
print(f"Second column of A: {A[:, 1]}")
```

### Matrix Multiplication: The Fundamental Operation

**Intuition**: Matrix multiplication is like applying a transformation. When you multiply matrix $A$ by matrix $B$, you're using $A$ to transform each column of $B$.

DIAGRAM: {"type": "matrix", "description": "Visual representation of matrix multiplication showing how rows of A combine with columns of B", "components": ["Matrix A (2×3)", "Matrix B (3×2)", "Result C (2×2)", "Highlighted row-column dot products"]}

**The Rule**: To multiply $A_{m \times n}$ by $B_{n \times p}$:
1. The number of columns in $A$ must equal the number of rows in $B$
2. The result is an $m \times p$ matrix $C$
3. Each element $c_{ij}$ is the dot product of row $i$ from $A$ and column $j$ from $B$

**Formal Definition**:

$$(AB)_{ij} = \sum_{k=1}^{n} a_{ik}b_{kj}$$

Where:
- $i$ ranges from 1 to $m$ (rows of result)
- $j$ ranges from 1 to $p$ (columns of result)
- $k$ is the summation index

**Step-by-Step Example**:

Let's multiply:
$$A = \begin{bmatrix} 1 & 2 & 3 \\ 4 & 5 & 6 \end{bmatrix}, \quad B = \begin{bmatrix} 7 & 8 \\ 9 & 10 \\ 11 & 12 \end{bmatrix}$$

Result will be $2 \times 2$ (since $A$ is $2 \times 3$ and $B$ is $3 \times 2$):

$$C_{11} = (1)(7) + (2)(9) + (3)(11) = 7 + 18 + 33 = 58$$
$$C_{12} = (1)(8) + (2)(10) + (3)(12) = 8 + 20 + 36 = 64$$
$$C_{21} = (4)(7) + (5)(9) + (6)(11) = 28 + 45 + 66 = 139$$
$$C_{22} = (4)(8) + (5)(10) + (6)(12) = 32 + 50 + 72 = 154$$

Therefore: $C = \begin{bmatrix} 58 & 64 \\ 139 & 154 \end{bmatrix}$

```python
# Matrix multiplication in Python
A = np.array([[1, 2, 3], 
              [4, 5, 6]])

B = np.array([[7, 8], 
              [9, 10], 
              [11, 12]])

# Method 1: Using @ operator (recommended)
C = A @ B
print("A @ B =")
print(C)

# Method 2: Using np.dot
C_dot = np.dot(A, B)
print("\nnp.dot(A, B) =")
print(C_dot)

# Method 3: Manual implementation to understand the algorithm
def manual_matmul(A, B):
    """Manually compute matrix multiplication to understand the process"""
    m, n = A.shape      # A is m × n
    n2, p = B.shape     # B is n × p
    
    if n != n2:
        raise ValueError(f"Cannot multiply {m}×{n} by {n2}×{p}")
    
    # Initialize result matrix with zeros
    C = np.zeros((m, p))
    
    # Triple nested loop implementation
    for i in range(m):          # For each row of A
        for j in range(p):      # For each column of B
            for k in range(n):  # Compute dot product
                C[i, j] += A[i, k] * B[k, j]
    
    return C

C_manual = manual_matmul(A, B)
print("\nManual multiplication =")
print(C_manual)

# Verify all methods give same result
print(f"\nAll methods equal? {np.allclose(C, C_dot) and np.allclose(C, C_manual)}")
```

### Properties of Matrix Multiplication

Unlike regular multiplication, matrix multiplication has unique properties:

#### 1. **Non-Commutative**: $AB \neq BA$ (order matters!)

```python
# Demonstrating non-commutativity
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

AB = A @ B
BA = B @ A

print("A @ B =")
print(AB)
print("\nB @ A =") 
print(BA)
print(f"\nAre they equal? {np.array_equal(AB, BA)}")
```

#### 2. **Associative**: $(AB)C = A(BC)$

```python
# Demonstrating associativity
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
C = np.array([[9, 10], [11, 12]])

left = (A @ B) @ C
right = A @ (B @ C)

print("(A @ B) @ C =")
print(left)
print("\nA @ (B @ C) =")
print(right)
print(f"\nAre they equal? {np.allclose(left, right)}")
```

#### 3. **Distributive**: $A(B + C) = AB + AC$

#### 4. **Identity Matrix**: $AI = IA = A$ where $I$ is the identity matrix

```python
# Identity matrix property
A = np.array([[1, 2, 3], [4, 5, 6]])
I_left = np.eye(2)   # 2×2 identity for left multiplication
I_right = np.eye(3)  # 3×3 identity for right multiplication

print("A =")
print(A)
print(f"\nI_left @ A = \n{I_left @ A}")
print(f"\nA @ I_right = \n{A @ I_right}")
```

### Special Matrices in ML

#### 1. **Identity Matrix**: Diagonal of 1s, 0s elsewhere
$$I_n = \begin{bmatrix}
1 & 0 & \cdots & 0 \\
0 & 1 & \cdots & 0 \\
\vdots & \vdots & \ddots & \vdots \\
0 & 0 & \cdots & 1
\end{bmatrix}$$

**ML Use**: Initialization, regularization (adding $\lambda I$ to matrices)

#### 2. **Diagonal Matrix**: Non-zero elements only on diagonal
$$D = \begin{bmatrix}
d_1 & 0 & \cdots & 0 \\
0 & d_2 & \cdots & 0 \\
\vdots & \vdots & \ddots & \vdots \\
0 & 0 & \cdots & d_n
\end{bmatrix}$$

**ML Use**: Scaling transformations, covariance matrices in Gaussian distributions

#### 3. **Symmetric Matrix**: $A = A^T$ (equals its transpose)

**ML Use**: Covariance matrices, gram matrices in kernels

```python
# Creating and using special matrices
# Identity matrix
I = np.eye(4)
print("Identity matrix:")
print(I)

# Diagonal matrix
d = [2, 3, 5, 7]
D = np.diag(d)
print("\nDiagonal matrix from", d, ":")
print(D)

# Symmetric matrix
A = np.array([[1, 2, 3], [2, 4, 5], [3, 5, 6]])
print("\nSymmetric matrix (A = A.T):")
print(A)
print(f"Is symmetric? {np.allclose(A, A.T)}")

# Demonstrating diagonal matrix multiplication (scaling)
v = np.array([1, 1, 1, 1])
scaled = D @ v
print(f"\nScaling vector {v} by diagonal matrix: {scaled}")
```

### Matrix as Linear Transformation

One of the most powerful interpretations of matrix multiplication is as a **linear transformation**. When we multiply a matrix by a vector, we transform that vector into a new space.

DIAGRAM: {"type": "plot", "description": "2D visualization showing how a matrix transforms unit vectors and a grid", "components": ["Original grid", "Transformed grid", "Unit vectors before/after", "Transformation matrix"]}

```python
# Visualizing matrix as transformation
def plot_transformation(A, title="Matrix Transformation"):
    """Visualize how matrix A transforms 2D space"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Create grid of points
    x = np.linspace(-2, 2, 10)
    y = np.linspace(-2, 2, 10)
    
    # Original unit vectors
    origin = np.zeros(2)
    i_hat = np.array([1, 0])
    j_hat = np.array([0, 1])
    
    # Plot original space
    ax1.set_title("Original Space")
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0, color='k', linewidth=0.5)
    ax1.axvline(x=0, color='k', linewidth=0.5)
    
    # Plot grid lines
    for xi in x:
        ax1.plot([xi, xi], [-2, 2], 'gray', alpha=0.3)
    for yi in y:
        ax1.plot([-2, 2], [yi, yi], 'gray', alpha=0.3)
    
    # Plot unit vectors
    ax1.quiver(0, 0, i_hat[0], i_hat[1], angles='xy', scale_units='xy', 
               scale=1, color='red', width=0.01)
    ax1.quiver(0, 0, j_hat[0], j_hat[1], angles='xy', scale_units='xy', 
               scale=1, color='blue', width=0.01)
    ax1.set_xlim(-3, 3)
    ax1.set_ylim(-3, 3)
    ax1.set_aspect('equal')
    
    # Transform unit vectors
    i_hat_transformed = A @ i_hat
    j_hat_transformed = A @ j_hat
    
    # Plot transformed space
    ax2.set_title(f"Transformed Space\n{title}")
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0, color='k', linewidth=0.5)
    ax2.axvline(x=0, color='k', linewidth=0.5)
    
    # Plot transformed grid
    for xi in x:
        points = np.array([[xi, yi] for yi in y]).T
        transformed = A @ points
        ax2.plot(transformed[0, :], transformed[1, :], 'gray', alpha=0.3)
    
    for yi in y:
        points = np.array([[xi, yi] for xi in x]).T
        transformed = A @ points
        ax2.plot(transformed[0, :], transformed[1, :], 'gray', alpha=0.3)
    
    # Plot transformed unit vectors
    ax2.quiver(0, 0, i_hat_transformed[0], i_hat_transformed[1], 
               angles='xy', scale_units='xy', scale=1, color='red', width=0.01)
    ax2.quiver(0, 0, j_hat_transformed[0], j_hat_transformed[1], 
               angles='xy', scale_units='xy', scale=1, color='blue', width=0.01)
    ax2.set_xlim(-3, 3)
    ax2.set_ylim(-3, 3)
    ax2.set_aspect('equal')
    
    plt.tight_layout()
    return fig

# Examples of different transformations
# Rotation by 45 degrees
theta = np.pi/4
rotation = np.array([[np.cos(theta), -np.sin(theta)],
                     [np.sin(theta), np.cos(theta)]])
plot_transformation(rotation, "Rotation by 45°")
plt.show()

# Scaling transformation
scaling = np.array([[2, 0], [0, 0.5]])
plot_transformation(scaling, "Scale x by 2, y by 0.5")
plt.show()

# Shear transformation
shear = np.array([[1, 0.5], [0, 1]])
plot_transformation(shear, "Shear transformation")
plt.show()
```

### Matrix Operations for Batch Processing

In ML, we often need to process multiple data points simultaneously. Matrix multiplication enables efficient batch operations:

```python
# Batch processing example
# Suppose we have 100 data points, each with 3 features
batch_size = 100
input_dim = 3
output_dim = 2

# Random batch of input data
X = np.random.randn(batch_size, input_dim)
print(f"Input batch shape: {X.shape}")

# Weight matrix for transformation
W = np.random.randn(input_dim, output_dim)
print(f"Weight matrix shape: {W.shape}")

# Bias vector
b = np.random.randn(output_dim)
print(f"Bias vector shape: {b.shape}")

# Transform entire batch at once!
Y = X @ W + b  # Broadcasting adds b to each row
print(f"Output batch shape: {Y.shape}")

# This is equivalent to processing each sample individually:
Y_slow = np.zeros((batch_size, output_dim))
for i in range(batch_size):
    Y_slow[i] = X[i] @ W + b

print(f"\nBatch processing matches individual processing: {np.allclose(Y, Y_slow)}")

# Timing comparison
import time

# Large batch
big_batch = 10000
X_big = np.random.randn(big_batch, input_dim)

# Batch processing
start = time.time()
Y_batch = X_big @ W + b
batch_time = time.time() - start

# Individual processing
start = time.time()
Y_individual = np.zeros((big_batch, output_dim))
for i in range(big_batch):
    Y_individual[i] = X_big[i] @ W + b
individual_time = time.time() - start

print(f"\nBatch processing time: {batch_time:.4f}s")
print(f"Individual processing time: {individual_time:.4f}s")
print(f"Speedup: {individual_time/batch_time:.1f}x")
```

## Worked Examples

### Example 1: Neural Network Forward Pass

Let's implement a simple 2-layer neural network forward pass using matrix multiplication.

**Problem**: Given input data with 4 features, create a neural network that:
1. First layer: transforms 4 features to 3 hidden units
2. Second layer: transforms 3 hidden units to 2 outputs
3. Uses ReLU activation between layers

```python
# Complete neural network forward pass example
import numpy as np

# Define network architecture
input_dim = 4
hidden_dim = 3
output_dim = 2

# Initialize weights and biases
# Using Xavier initialization (good practice)
np.random.seed(42)  # For reproducibility
W1 = np.random.randn(input_dim, hidden_dim) * np.sqrt(2.0 / input_dim)
b1 = np.zeros(hidden_dim)
W2 = np.random.randn(hidden_dim, output_dim) * np.sqrt(2.0 / hidden_dim)
b2 = np.zeros(output_dim)

print("Network Architecture:")
print(f"Layer 1: {input_dim} → {hidden_dim}")
print(f"Layer 2: {hidden_dim} → {output_dim}")
print(f"\nW1 shape: {W1.shape}")
print(f"W2 shape: {W2.shape}")

# Define activation function
def relu(x):
    """ReLU activation: max(0, x)"""
    return np.maximum(0, x)

# Sample input (batch of 5 samples)
X = np.array([
    [1.0, 0.5, -0.3, 0.8],
    [0.2, -0.1, 0.7, 0.4],
    [-0.5, 0.3, 0.9, -0.2],
    [0.8, 0.8, -0.6, 0.3],
    [0.1, -0.7, 0.4, 0.9]
])

print(f"\nInput shape: {X.shape}")

# Forward pass - Step by step
print("\n--- FORWARD PASS ---")

# Step 1: First linear transformation
Z1 = X @ W1 + b1
print(f"\nStep 1 - First linear layer:")
print(f"Z1 = X @ W1 + b1")
print(f"Z1 shape: {Z1.shape}")
print(f"Z1 (first sample):\n{Z1[0]}")

# Step 2: Apply activation
H1 = relu(Z1)
print(f"\nStep 2 - ReLU activation:")
print(f"H1 = relu(Z1)")
print(f"H1 (first sample):\n{H1[0]}")

# Step 3: Second linear transformation
Z2 = H1 @ W2 + b2
print(f"\nStep 3 - Second linear layer:")
print(f"Z2 = H1 @ W2 + b2")
print(f"Z2 shape: {Z2.shape}")
print(f"Z2 (first sample):\n{Z2[0]}")

# Complete forward pass as a function
def forward_pass(X, W1, b1, W2, b2):
    """Complete forward pass through 2-layer network"""
    # Layer 1
    Z1 = X @ W1 + b1
    H1 = relu(Z1)
    
    # Layer 2
    Z2 = H1 @ W2 + b2
    
    # Return output and intermediates (useful for backprop)
    return Z2, (Z1, H1)

# Verify our function
output, _ = forward_pass(X, W1, b1, W2, b2)
print(f"\nFinal output shape: {output.shape}")
print(f"Output for all samples:\n{output}")
```

### Example 2: Image Transformation with Matrices

Let's see how matrices can transform images, demonstrating their power in computer vision applications.

```python
# Image transformation example
import numpy as np
import matplotlib.pyplot as plt

# Create a simple 5x5 "image" 
image = np.array([
    [0, 0, 1, 0, 0],
    [0, 1, 1, 1, 0],
    [1, 1, 1, 1, 1],
    [0, 1, 1, 1, 0],
    [0, 0, 1, 0, 0]
])

print("Original image (diamond shape):")
print(image)

# Convert image to coordinate points
points = []
for i in range(5):
    for j in range(5):
        if image[i, j] == 1:
            # Store as (x, y) where x is column, y is row
            # Shift to center around origin
            points.append([j - 2, 2 - i])

points = np.array(points).T  # Shape: (2, num_points)
print(f"\nNumber of points: {points.shape[1]}")

# Define transformation matrices
# 1. Rotation by 30 degrees
theta = np.pi / 6  # 30 degrees
rotation_matrix = np.array([
    [np.cos(theta), -np.sin(theta)],
    [np.sin(theta), np.cos(theta)]
])

# 2. Scaling (stretch x by 1.5, shrink y by 0.8)
scale_matrix = np.array([
    [1.5, 0],
    [0, 0.8]
])

# 3. Shear transformation
shear_matrix = np.array([
    [1, 0.3],
    [0.2, 1]
])

# 4. Reflection across y-axis
reflection_matrix = np.array([
    [-1, 0],
    [0, 1]
])

# Apply transformations
rotated_points = rotation_matrix @ points
scaled_points = scale_matrix @ points
sheared_points = shear_matrix @ points
reflected_points = reflection_matrix @ points

# Composition: rotation then scaling
composed_points = scale_matrix @ (rotation_matrix @ points)

# Plotting
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()

# Helper function to plot points
def plot_points(ax, points, title, color='blue'):
    ax.scatter(points[0, :], points[1, :], s=100, c=color, alpha=0.6)
    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', linewidth=0.5)
    ax.axvline(x=0, color='k', linewidth=0.5)
    ax.set_aspect('equal')
    ax.set_title(title)

# Plot all transformations
plot_points(axes[0], points, "Original", 'black')
plot_points(axes[1], rotated_points, f"Rotated by 30°", 'red')
plot_points(axes[2], scaled_points, "Scaled (x×1.5, y×0.8)", 'green')
plot_points(axes[3], sheared_points, "Sheared", 'blue')
plot_points(axes[4], reflected_points, "Reflected (y-axis)", 'purple')
plot_points(axes[5], composed_points, "Rotated then Scaled", 'orange')

plt.tight_layout()
plt.show()

# Demonstrate matrix composition
print("\nMatrix Composition:")
print("Rotation matrix @ Scale matrix ≠ Scale matrix @ Rotation matrix")
comp1 = scale_matrix @ rotation_matrix
comp2 = rotation_matrix @ scale_matrix
print(f"Scale @ Rotation:\n{comp1}")
print(f"Rotation @ Scale:\n{comp2}")
print(f"Are they equal? {np.allclose(comp1, comp2)}")
```

### Example 3: Solving Linear Systems with Matrices

Many ML algorithms involve solving linear systems. Let's see how matrix operations help.

```python
# Linear system solving example
# Problem: Find weights that best fit data (simplified linear regression)

# Generate synthetic data
np.random.seed(42)
n_samples = 50
n_features = 3

# True weights
true_weights = np.array([2.5, -1.3, 0.7])
true_bias = 1.5

# Generate random features
X = np.random.randn(n_samples, n_features)

# Add bias term (column of ones)
X_with_bias = np.column_stack([np.ones(n_samples), X])

# Generate targets (with some noise)
true_params = np.concatenate([[true_bias], true_weights])
y = X_with_bias @ true_params + 0.1 * np.random.randn(n_samples)

print("Problem: Find w such that Xw ≈ y")
print(f"X shape: {X_with_bias.shape}")
print(f"y shape: {y.shape}")
print(f"True parameters: {true_params}")

# Method 1: Normal equation (closed-form solution)
# w = (X^T X)^(-1) X^T y
print("\n--- Method 1: Normal Equation ---")

# Step by step
XtX = X_with_bias.T @ X_with_bias
print(f"X^T X shape: {XtX.shape}")

Xty = X_with_bias.T @ y
print(f"X^T y shape: {Xty.shape}")

# Solve using inverse
XtX_inv = np.linalg.inv(XtX)
w_normal = XtX_inv @ Xty
print(f"\nEstimated parameters: {w_normal}")
print(f"True parameters:      {true_params}")
print(f"Error: {np.linalg.norm(w_normal - true_params):.4f}")

# Method 2: Using NumPy's solver (more numerically stable)
print("\n--- Method 2: NumPy Solver ---")
w_solver, residuals, rank, s = np.linalg.lstsq(X_with_bias, y, rcond=None)
print(f"Estimated parameters: {w_solver}")
print(f"Residual sum of squares: {residuals[0]:.4f}")

# Visualize the fit
predictions = X_with_bias @ w_normal

plt.figure(figsize=(10, 4))

# Plot 1: Predictions vs Actual
plt.subplot(1, 2, 1)
plt.scatter(y, predictions, alpha=0.6)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', label='Perfect fit')
plt.xlabel('Actual values')
plt.ylabel('Predicted values')
plt.title('Predictions vs Actual')
plt.legend()

# Plot 2: Residuals
plt.subplot(1, 2, 2)
residuals = y - predictions
plt.scatter(predictions, residuals, alpha=0.6)
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Predicted values')
plt.ylabel('Residuals')
plt.title('Residual Plot')

plt.tight_layout()
plt.show()

# Matrix condition number (numerical stability indicator)
print(f"\nCondition number of X^T X: {np.linalg.cond(XtX):.2f}")
print("(Lower is better - high values indicate numerical instability)")
```

## Common Pitfalls

When learning matrix multiplication, students often encounter these challenges:

### 1. **Dimension Mismatch Errors**

The most common error is trying to multiply incompatible matrices:

```python
# Common dimension errors and how to debug them
A = np.array([[1, 2, 3], [4, 5, 6]])      # Shape: (2, 3)
B = np.array([[7, 8], [9, 10]])           # Shape: (2, 2)

# This will fail!
try:
    C = A @ B
except ValueError as e:
    print(f"Error: {e}")
    print(f"A shape: {A.shape}, B shape: {B.shape}")
    print(f"Can't multiply (2,3) × (2,2) - inner dimensions don't match!")
    print("\nFix: Need B to have 3 rows, or transpose A")

# Solution 1: Use correct B
B_correct = np.array([[7, 8], [9, 10], [11, 12]])  # Shape: (3, 2)
C = A @ B_correct
print(f"\nA @ B_correct works: {A.shape} × {B_correct.shape} → {C.shape}")

# Solution 2: Transpose if needed
C_alt = A.T @ B  # (3, 2) × (2, 2) → (3, 2)
print(f"A.T @ B works: {A.T.shape} × {B.shape} → {C_alt.shape}")
```

### 2. **Confusing Element-wise and Matrix Multiplication**

```python
# Element-wise vs Matrix multiplication
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

# Element-wise multiplication (Hadamard product)
elementwise = A * B
print("Element-wise (A * B):")
print(elementwise)

# Matrix multiplication
matrix_mult = A @ B
print("\nMatrix multiplication (A @ B):")
print(matrix_mult)

print("\nThey're different operations with different results!")
```

### 3. **Broadcasting Confusion**

```python
# Understanding broadcasting with matrices
A = np.array([[1, 2, 3], [4, 5, 6]])     # Shape: (2, 3)
b = np.array([10, 20, 30])                # Shape: (3,)

# This works due to broadcasting
result1 = A + b  # b is broadcast to each row
print("A + b (broadcasting):")
print(result1)

# But this is different from matrix multiplication
result2 = A @ b  # Matrix-vector multiplication
print(f"\nA @ b (matrix multiplication): {result2}")
print(f"Result shape: {result2.shape}")

# Common mistake: expecting (2,3) output
# But matrix mult gives (2,) output!
```

### 4. **Forgetting Non-Commutativity**

```python
# Order matters in matrix multiplication!
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

# In neural networks, this mistake can be catastrophic
W = np.random.randn(10, 5)  # Weight matrix
x = np.random.randn(5)      # Input vector

# Correct: W @ x
correct = W @ x  # Shape: (10,)

# Wrong: x @ W would fail!
try:
    wrong = x @ W
except ValueError as e:
    print(f"Error with x @ W: {e}")
    print("Remember: weights typically go first!")
```

### 5. **Inefficient Implementations**

```python
# Inefficient vs efficient matrix operations

# Bad: Using loops for matrix operations
def bad_matrix_mult(A, B):
    result = []
    for i in range(len(A)):
        row = []
        for j in range(len(B[0])):
            sum_val = 0
            for k in range(len(B)):
                sum_val += A[i][k] * B[k][j]
            row.append(sum_val)
        result.append(row)
    return np.array(result)

# Good: Use NumPy's optimized operations
def good_matrix_mult(A, B):
    return A @ B

# Timing comparison
A = np.random.randn(100, 100)
B = np.random.randn(100, 100)

import time
start = time.time()
bad_result = bad_matrix_mult(A.tolist(), B.tolist())
bad_time = time.time() - start

start = time.time()
good_result = good_matrix_mult(A, B)
good_time = time.time() - start

print(f"Loop implementation: {bad_time:.4f}s")
print(f"NumPy implementation: {good_time:.4f}s")
print(f"Speedup: {bad_time/good_time:.1f}x")
```

## Summary & Key Takeaways

Today we mastered matrices and matrix multiplication — the computational backbone of machine learning. Here are the essential points to remember:

### Core Concepts
- **Matrix Definition**: A matrix is a 2D array with $m$ rows and $n$ columns, denoted as $m \times n$
- **Matrix Multiplication Rule**: To multiply $A_{m \times n} \times B_{n \times p} = C_{m \times p}$, inner dimensions must match
- **Each element**: $C_{ij} = \sum_{k=1}^{n} A_{ik}B_{kj}$ (dot product of row $i$ from $A$ with column $j$ from $B$)

### Key Properties
- **Non-commutative**: $AB \neq BA$ (order matters!)
- **Associative**: $(AB)C = A(BC)$
- **Distributive**: $A(B + C) = AB + AC$
- **Identity**: $AI = IA = A$

### Essential Python Operations
```python
# Creating matrices
A = np.array([[1, 2], [3, 4]])

# Matrix multiplication
C = A @ B              # Recommended
C = np.dot(A, B)      # Alternative
C = A.dot(B)          # Method syntax

# Special matrices
I = np.eye(n)         # Identity matrix
D = np.diag([...])    # Diagonal matrix
Z = np.zeros((m, n))  # Zero matrix
```

### ML Applications
1. **Neural Networks**: Weight matrices transform inputs through layers
2. **Batch Processing**: Process multiple samples simultaneously
3. **Linear Transformations**: Rotations, scaling, projections
4. **Linear Systems**: Solving for optimal parameters

### Key Formulas Reference
- Matrix multiplication: $(AB)_{ij} = \sum_{k=1}^{n} a_{ik}b_{kj}$
- Neural network layer: $\mathbf{y} = \text{activation}(W\mathbf{x} + \mathbf{b})$
- Batch processing: $Y = XW + \mathbf{b}$ (broadcasting adds bias)
- Normal equation: $\mathbf{w} = (X^TX)^{-1}X^T\mathbf{y}$

### Debugging Checklist
- ✓ Check matrix dimensions before multiplication
- ✓ Remember order matters (AB ≠ BA)
- ✓ Use @ operator for matrix multiplication, * for element-wise
- ✓ Verify shapes with `.shape` attribute
- ✓ Use NumPy operations instead of loops

## Tomorrow's Preview

Having mastered matrix multiplication, we're ready to explore **Norms and Distances** — fundamental concepts for measuring the "size" of vectors and the "distance" between points. These concepts are crucial for:

- Understanding regularization (L1 and L2 norms)
- Implementing k-nearest neighbors algorithms
- Measuring model performance and convergence
- Optimization and gradient descent

Questions to ponder:
1. How do we measure the "length" of a vector with multiple dimensions?
2. What does it mean for two data points to be "close" in high-dimensional space?
3. Why might different distance metrics give different results in ML algorithms?

Tomorrow's episode will give you the mathematical tools to answer these questions and understand how modern ML algorithms measure similarity and difference in data. Get ready to explore the geometry of machine learning!