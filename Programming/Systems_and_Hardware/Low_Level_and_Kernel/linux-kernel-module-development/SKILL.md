---
name: linux-kernel-module-development
metadata:
  category: Low-Level Systems Drivers and Kernel
description: Develop production-grade Linux Kernel Modules (LKM), character device drivers (`cdev`), and hardware control abstractions in C. Implement file operations (`open`, `read`, `write`, `unlocked_ioctl`), kernel memory allocators (`kmalloc`, `vmalloc`), spinlocks, mutexes, interrupt request handlers (bottom halves / tasklets), and sysfs attributes. Trigger when writing kernel drivers, low-level hardware interfaces, or debugging kernel crashes.
compatibility: Linux Kernel 5.x / 6.x, GCC / Clang, Kbuild Makefile system
---

# Linux Kernel Module Development Skill Guide

This skill governs the development, memory management, synchronization, and debugging of loadable kernel modules (LKMs) and character device drivers in Linux.

---

## 1. Kernel Space vs User Space Architecture

```text
[ User Space Application ]
       |
       |-- open("/dev/mydevice", O_RDWR);
       |-- ioctl(fd, CUSTOM_IOCTL_CMD, &payload);
       |
======================= System Call Boundary =======================
       |
[ Linux Kernel Space: VFS (Virtual File System) ]
       |
       v
[ Character Device Driver (cdev) ]
  |-- file_operations struct { .read, .write, .unlocked_ioctl }
  |-- Concurrency Protection (Spinlocks for atomic context, Mutex for sleeping)
  |-- Memory Access Safety (copy_to_user / copy_from_user)
       |
       v
[ Physical Hardware / Memory Mapped I/O (ioremap) ]
```

---

## 2. Production C Kernel Driver Implementation

### A. Character Device Driver with ioctl & copy_to_user

```c
#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/uaccess.h>
#include <linux/mutex.h>

#define DEVICE_NAME "custom_telemetry_dev"
#define IOCTL_MAGIC 'k'
#define IOCTL_GET_STATUS _IOR(IOCTL_MAGIC, 1, int)

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Senior Systems Engineer");
MODULE_DESCRIPTION("Hardened Character Device Driver with ioctl");
MODULE_VERSION("1.0");

static dev_t dev_number;
static struct cdev char_cdev;
static struct class *dev_class = NULL;
static DEFINE_MUTEX(dev_mutex);
static int device_status = 42;

static int dev_open(struct inode *inodep, struct file *filep) {
    if (!mutex_trylock(&dev_mutex)) {
        pr_warn("%s: Device is currently busy\\n", DEVICE_NAME);
        return -EBUSY;
    }
    pr_info("%s: Device opened successfully\\n", DEVICE_NAME);
    return 0;
}

static int dev_release(struct inode *inodep, struct file *filep) {
    mutex_unlock(&dev_mutex);
    pr_info("%s: Device closed\\n", DEVICE_NAME);
    return 0;
}

static long dev_ioctl(struct file *filep, unsigned int cmd, unsigned long arg) {
    switch (cmd) {
        case IOCTL_GET_STATUS:
            // Safely transfer data from kernel space to user space buffer
            if (copy_to_user((int __user *)arg, &device_status, sizeof(device_status))) {
                return -EFAULT;
            }
            break;
        default:
            return -EINVAL;
    }
    return 0;
}

static struct file_operations fops = {
    .owner = THIS_MODULE,
    .open = dev_open,
    .release = dev_release,
    .unlocked_ioctl = dev_ioctl,
};

static int __init custom_dev_init(void) {
    int ret;
    ret = alloc_chrdev_region(&dev_number, 0, 1, DEVICE_NAME);
    if (ret < 0) {
        pr_err("%s: Failed to allocate major number\\n", DEVICE_NAME);
        return ret;
    }

    cdev_init(&char_cdev, &fops);
    char_cdev.owner = THIS_MODULE;

    ret = cdev_add(&char_cdev, dev_number, 1);
    if (ret < 0) {
        unregister_chrdev_region(dev_number, 1);
        pr_err("%s: Failed to add cdev\\n", DEVICE_NAME);
        return ret;
    }

    pr_info("%s: Initialized with Major %d, Minor %d\\n", DEVICE_NAME, MAJOR(dev_number), MINOR(dev_number));
    return 0;
}

static void __exit custom_dev_exit(void) {
    cdev_del(&char_cdev);
    unregister_chrdev_region(dev_number, 1);
    pr_info("%s: Unloaded\\n", DEVICE_NAME);
}

module_init(custom_dev_init);
module_exit(custom_dev_exit);
```

### B. Standard Kbuild Makefile

```makefile
obj-m += custom_telemetry_dev.o

KDIR ?= /lib/modules/$(shell uname -r)/build

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
```

---

## 3. Kernel Safety Checklist

- [ ] **No Direct Pointer Dereferencing:** NEVER dereference user-space pointers directly in kernel space; always use `copy_to_user()` and `copy_from_user()`.
- [ ] **No Sleeping in Atomic Context:** Never call functions that can sleep (such as `mutex_lock`, `msleep`, or `kmalloc(..., GFP_KERNEL)`) inside interrupt handlers or while holding a spinlock. Use `kmalloc(..., GFP_ATOMIC)` and spinlocks instead.
- [ ] **Check Return Values:** Always check `copy_to_user` return value; non-zero indicates memory fault (`-EFAULT`).
