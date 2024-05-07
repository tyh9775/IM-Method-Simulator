import numpy as np
import matplotlib.pyplot as plt

# Define the function
def my_function(x, y):
    return np.sin(x) + np.cos(y)

# Generate data
x = np.linspace(0, 2*np.pi, 100)
y = np.linspace(0, 2*np.pi, 100)
X, Y = np.meshgrid(x, y)
Z = my_function(X, Y)

# Create contour plot
plt.figure(figsize=(8, 6))
contour = plt.contourf(X, Y, Z, cmap='viridis')
plt.colorbar(contour, label='Function Value')

# Add labels and title
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Contour Plot of My Function')

# Show plot
plt.show()
