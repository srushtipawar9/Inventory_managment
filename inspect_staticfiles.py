import os
root = r'D:\inventory_2\staticfiles'
print('exists', os.path.exists(root))
print('isdir', os.path.isdir(root))
for dirpath, dirnames, filenames in os.walk(root):
    print('DIR', dirpath)
    for f in filenames:
        print('FILE', os.path.join(dirpath, f))
