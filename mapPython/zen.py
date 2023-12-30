import inspect 
import this

f = inspect.getsourcefile(this)
print(f)
print()
print(inspect.getsource(this))