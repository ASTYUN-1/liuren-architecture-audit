class DragManager {
    constructor() {
        this.isDragging = false;
        this.currentElement = null;
        this.startX = 0;
        this.startY = 0;
        this.startLeft = 0;
        this.startTop = 0;
        this.initialPosition = new Map(); // 存储元素初始定位方式
        this.initialOffset = new Map(); // 存储元素初始偏移
        this.eventHandlers = new Map();
        this.isClick = true; // 标记是否为点击事件
        this.dragThreshold = 5; // 拖拽阈值(px)

        this.init();
    }

    /**
     * 初始化拖拽管理器
     */
    init() {
        this.bindGlobalEvents();
        // console.log('拖拽管理器已初始化 - 支持触摸和鼠标事件');
    }

    /**
     * 绑定全局事件监听器
     */
    bindGlobalEvents() {
        // 使用被动事件监听器提高性能
        const options = { passive: false, capture: true };

        // 绑定开始事件
        document.addEventListener('mousedown', this.handleStart.bind(this), options);
        document.addEventListener('touchstart', this.handleStart.bind(this), { passive: false, capture: true });

        // 绑定移动事件
        document.addEventListener('mousemove', this.handleMove.bind(this), options);
        document.addEventListener('touchmove', this.handleMove.bind(this), { passive: false, capture: true });

        // 绑定结束事件
        document.addEventListener('mouseup', this.handleEnd.bind(this), options);
        document.addEventListener('touchend', this.handleEnd.bind(this), { passive: false, capture: true });
        document.addEventListener('touchcancel', this.handleEnd.bind(this));

        // 窗口失去焦点时强制结束拖拽
        window.addEventListener('blur', this.handleEnd.bind(this));
    }

    /**
     * 解除所有事件绑定
     */
    destroy() {
        const events = [
            'mousedown', 'touchstart',
            'mousemove', 'touchmove',
            'mouseup', 'touchend', 'touchcancel'
        ];

        // 解绑所有全局事件
        events.forEach(event => {
            document.removeEventListener(event, this.handleStart.bind(this));
            document.removeEventListener(event, this.handleMove.bind(this));
            document.removeEventListener(event, this.handleEnd.bind(this));
        });

        window.removeEventListener('blur', this.handleEnd.bind(this));

        // 清除所有元素的拖拽状态
        document.querySelectorAll('.draggable').forEach(el => {
            this.makeUndraggable(el);
        });

        console.log('拖拽管理器已销毁');
    }

    /**
     * 拖拽开始事件处理
     */
    handleStart(event) {
        // 寻找最近的.draggable元素
        const target = event.target.closest('.draggable');
        if (!target) return;

        // 记录初始点击状态
        this.isClick = true;

        // 获取起始坐标
        const coords = this.getEventCoordinates(event);
        this.startX = coords.clientX;
        this.startY = coords.clientY;

        this.isDragging = true;
        this.currentElement = target;

        // 计算初始位置（基于定位父元素）
        const rect = target.getBoundingClientRect();
        const offsetParent = target.offsetParent;
        const offsetRect = offsetParent ? offsetParent.getBoundingClientRect() : { left: 0, top: 0 };

        // 存储相对于定位父元素的偏移量
        this.startLeft = rect.left - offsetRect.left;
        this.startTop = rect.top - offsetRect.top;

        // 添加拖拽样式
        target.classList.add('dragging');

        console.log('拖拽开始:', target.id || '匿名元素', { x: this.startX, y: this.startY });
    }

    /**
     * 拖拽移动事件处理
     */
    handleMove(event) {
        if (!this.isDragging || !this.currentElement) return;

        const coords = this.getEventCoordinates(event);
        const deltaX = coords.clientX - this.startX;
        const deltaY = coords.clientY - this.startY;

        // 判断是否超过拖拽阈值
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
        if (distance > this.dragThreshold) {
            this.isClick = false; // 超过阈值则视为拖拽而非点击
            event.preventDefault(); // 只有确定是拖拽时才阻止默认行为
        } else {
            return; // 未超过阈值不处理移动
        }

        // 计算新位置（基于定位父元素）
        const offsetParent = this.currentElement.offsetParent;
        const offsetRect = offsetParent ? offsetParent.getBoundingClientRect() : { left: 0, top: 0 };
        const newLeft = this.startLeft + deltaX;
        const newTop = this.startTop + deltaY;

        // 应用新位置
        this.currentElement.style.left = newLeft + 'px';
        this.currentElement.style.top = newTop + 'px';

        // 限制在视口内（可选）
        this.keepInViewport(this.currentElement);
    }

    /**
     * 拖拽结束事件处理
     */
    handleEnd(event) {
        if (!this.isDragging || !this.currentElement) return;

        this.isDragging = false;

        // 移除拖拽样式
        this.currentElement.classList.remove('dragging');

        // 如果是点击事件且是触摸结束，手动触发点击
        if (this.isClick && event.type === 'touchend') {
            const touchTarget = event.target;
            if (touchTarget) {
                const clickEvent = new MouseEvent('click', {
                    bubbles: true,
                    cancelable: true,
                    view: window
                });
                touchTarget.dispatchEvent(clickEvent);
            }
        }

        console.log('拖拽结束:', this.currentElement.id || '匿名元素');
        this.currentElement = null;
    }

    /**
     * 获取事件坐标（兼容触摸和鼠标事件）
     */
    getEventCoordinates(event) {
        if (event.touches && event.touches.length > 0) {
            return {
                clientX: event.touches[0].clientX,
                clientY: event.touches[0].clientY
            };
        } else {
            return {
                clientX: event.clientX,
                clientY: event.clientY
            };
        }
    }

    /**
     * 确保元素不会移出视口
     */
    keepInViewport(element) {
        const rect = element.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;

        // 计算元素可移动的最大范围
        const maxLeft = viewportWidth - rect.width;
        const maxTop = viewportHeight - rect.height;

        // 获取当前相对于视口的位置
        let currentLeft = rect.left;
        let currentTop = rect.top;

        // 限制在视口内（允许在视口范围内自由移动）
        currentLeft = Math.max(0, Math.min(currentLeft, maxLeft));
        currentTop = Math.max(0, Math.min(currentTop, maxTop));

        // 转换为相对于定位父元素的坐标
        const offsetParent = element.offsetParent;
        const offsetRect = offsetParent ? offsetParent.getBoundingClientRect() : { left: 0, top: 0 };

        // 应用修正后的位置
        element.style.left = (currentLeft - offsetRect.left) + 'px';
        element.style.top = (currentTop - offsetRect.top) + 'px';
    }

    /**
     * 使元素可拖拽
     */
    makeDraggable(element) {
        if (!element || !element.classList) {
            console.error('无效的元素');
            return;
        }

        // 记录原始定位方式（如果尚未记录）
        if (!this.initialPosition.has(element)) {
            const computedStyle = window.getComputedStyle(element);
            const position = computedStyle.position;
            this.initialPosition.set(element, position);

            // 存储元素在弹性盒子中的偏移
            this.initialOffset.set(element, {
                marginLeft: computedStyle.marginLeft,
                marginTop: computedStyle.marginTop,
                marginRight: computedStyle.marginRight,
                marginBottom: computedStyle.marginBottom
            });

            // 如果元素没有设置定位，强制设置为absolute以确保可拖拽
            if (!['absolute', 'fixed', 'relative'].includes(position)) {
                // 保存当前位置
                const rect = element.getBoundingClientRect();
                const offsetParent = element.offsetParent;
                const offsetRect = offsetParent ? offsetParent.getBoundingClientRect() : { left: 0, top: 0 };
                
                // 先设置为relative获取正确的offsetParent
                element.style.position = 'relative';
                const newOffsetParent = element.offsetParent;
                const newOffsetRect = newOffsetParent ? newOffsetParent.getBoundingClientRect() : { left: 0, top: 0 };

                // 计算相对于新offsetParent的位置
                const left = rect.left - newOffsetRect.left;
                const top = rect.top - newOffsetRect.top;

                // 最终设置为absolute并应用计算后的位置
                element.style.position = 'absolute';
                

                // setTimeout(() => {
                //     let FDSL = document.getElementsByClassName('draggable')
                //     element.style.position = 'fixed';
                //     element.style.left = '20px';
                //     element.style.transition = "top 0.5s ease"
                //     // console.log()
                //     if (FDSL.length == 1) {
                //         element.style.top = "20px"
                //     } else {
                //         console.log(FDSL[FDSL.length - 2])
                //         element.style.top = (Number(FDSL[FDSL.length - 2].style.top.split("px")[0]) + 50) + "px"
                //     }
                // }, 500)

                element.style.left = left + 'px';
                element.style.top = top + 'px';

                // 清除margin避免影响定位
                element.style.margin = '0';
            }
        }

        element.classList.add('draggable');
        console.log('元素已设置为可拖拽:', element.id || '匿名元素');
    }

    /**
     * 解除单个元素的拖拽功能
     */
    makeUndraggable(element) {
        if (!element || !element.classList) {
            console.error('无效的元素');
            return;
        }

        // 移除拖拽相关类
        element.classList.remove('draggable', 'dragging');

        // 还原初始定位方式和偏移
        if (this.initialPosition.has(element)) {
            element.style.position = this.initialPosition.get(element);
            this.initialPosition.delete(element);
        }

        if (this.initialOffset.has(element)) {
            const offsets = this.initialOffset.get(element);
            element.style.marginLeft = offsets.marginLeft;
            element.style.marginTop = offsets.marginTop;
            element.style.marginRight = offsets.marginRight;
            element.style.marginBottom = offsets.marginBottom;
            this.initialOffset.delete(element);
        }

        // 如果当前正在拖拽该元素，强制结束拖拽
        if (this.currentElement === element) {
            this.handleEnd();
        }

        console.log('元素已解除拖拽功能:', element.id || '匿名元素');
    }
}









/**
         * 滑动事件监听器
         * 监听PC端鼠标和移动端触摸手势（上滑、下滑、左滑、右滑）
         * @class SwipeListener
         */
class SwipeListener {
    /**
     * 创建滑动监听器实例
     * @param {HTMLElement} element - 要监听滑动事件的DOM元素
     * @param {Object} options - 配置选项
     * @param {number} options.minSwipeDistance - 最小滑动距离（像素），默认30
     * @param {number} options.maxSwipeTime - 最大滑动时间（毫秒），默认500
     */
    constructor(element, options = {}) {
        this.element = element;
        this.minSwipeDistance = options.minSwipeDistance || 30;
        this.maxSwipeTime = options.maxSwipeTime || 500;
        
        // 事件监听器数组
        this.listeners = {
            swipeUp: [],
            swipeDown: [],
            swipeLeft: [],
            swipeRight: []
        };
        
        // 滑动数据
        this.startX = 0;
        this.startY = 0;
        this.startTime = 0;
        this.isDragging = false;
        
        // 绑定事件处理函数（保持this指向）
        this.handleStart = this.handleStart.bind(this);
        this.handleMove = this.handleMove.bind(this);
        this.handleEnd = this.handleEnd.bind(this);
        
        // 初始化事件监听
        this.initEvents();
    }
    
    /**
     * 初始化事件监听
     * @private
     */
    initEvents() {
        // 触摸事件（移动端）
        this.element.addEventListener('touchstart', this.handleStart, { passive: true });
        this.element.addEventListener('touchmove', this.handleMove, { passive:true });
        this.element.addEventListener('touchend', this.handleEnd);
        
        // 鼠标事件（PC端）
        this.element.addEventListener('mousedown', this.handleStart);
        this.element.addEventListener('mousemove', this.handleMove);
        this.element.addEventListener('mouseup', this.handleEnd);
        this.element.addEventListener('mouseleave', this.handleEnd);
        
        // 防止拖拽选中文本
        this.element.addEventListener('dragstart', (e) => e.preventDefault());
    }
    
    /**
     * 处理滑动开始事件
     * @param {Event} e - 事件对象
     * @private
     */
    handleStart(e) {
        // 阻止默认行为避免不必要的页面滚动
        if (e.type === 'mousedown') {
            e.preventDefault();
        }
        
        const point = this.getEventPoint(e);
        
        this.startX = point.x;
        this.startY = point.y;
        this.startTime = Date.now();
        this.isDragging = true;
        
        // 添加激活样式
        this.element.style.opacity = '0.8';
    }
    
    /**
     * 处理滑动移动事件
     * @param {Event} e - 事件对象
     * @private
     */
    handleMove(e) {
        if (!this.isDragging) return;
        
        if (e.type === 'mousemove') {
            e.preventDefault();
        }
    }
    
    /**
     * 处理滑动结束事件
     * @param {Event} e - 事件对象
     * @private
     */
    handleEnd(e) {
        if (!this.isDragging) return;
        
        const point = this.getEventPoint(e);
        const endTime = Date.now();
        
        // 计算滑动距离和时间
        const deltaX = point.x - this.startX;
        const deltaY = point.y - this.startY;
        const elapsedTime = endTime - this.startTime;
        
        // 重置状态
        this.isDragging = false;
        this.element.style.opacity = '1';
        
        // 检查是否为有效滑动
        if (elapsedTime > this.maxSwipeTime) return;
        
        const absDeltaX = Math.abs(deltaX);
        const absDeltaY = Math.abs(deltaY);
        
        // 确定主要滑动方向（水平或垂直）
        if (absDeltaX > absDeltaY && absDeltaX > this.minSwipeDistance) {
            // 水平滑动
            if (deltaX > 0) {
                this.trigger('swipeRight', { deltaX, deltaY, elapsedTime });
            } else {
                this.trigger('swipeLeft', { deltaX, deltaY, elapsedTime });
            }
        } else if (absDeltaY > absDeltaX && absDeltaY > this.minSwipeDistance) {
            // 垂直滑动
            if (deltaY > 0) {
                this.trigger('swipeDown', { deltaX, deltaY, elapsedTime });
            } else {
                this.trigger('swipeUp', { deltaX, deltaY, elapsedTime });
            }
        }
    }
    
    /**
     * 从事件对象获取坐标点
     * @param {Event} e - 事件对象
     * @returns {Object} 包含x、y坐标的对象
     * @private
     */
    getEventPoint(e) {
        if (e.touches && e.touches.length > 0) {
            return {
                x: e.touches[0].clientX,
                y: e.touches[0].clientY
            };
        } else if (e.changedTouches && e.changedTouches.length > 0) {
            return {
                x: e.changedTouches[0].clientX,
                y: e.changedTouches[0].clientY
            };
        } else {
            return {
                x: e.clientX,
                y: e.clientY
            };
        }
    }
    
    /**
     * 触发指定类型的事件
     * @param {string} type - 事件类型
     * @param {Object} detail - 事件详情
     * @private
     */
    trigger(type, detail) {
        this.listeners[type].forEach(callback => {
            try {
                callback(detail);
            } catch (error) {
                console.error(`Error in ${type} event handler:`, error);
            }
        });
        
        // 也触发通用swipe事件
        if (this.listeners.swipe) {
            this.listeners.swipe.forEach(callback => {
                try {
                    callback({ type, ...detail });
                } catch (error) {
                    console.error('Error in swipe event handler:', error);
                }
            });
        }
    }
    
    /**
     * 添加事件监听器
     * @param {string} event - 事件类型：'swipeUp', 'swipeDown', 'swipeLeft', 'swipeRight', 'swipe'
     * @param {Function} callback - 回调函数
     */
    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }
    
    /**
     * 移除事件监听器
     * @param {string} event - 事件类型
     * @param {Function} callback - 要移除的回调函数
     */
    off(event, callback) {
        if (this.listeners[event]) {
            const index = this.listeners[event].indexOf(callback);
            if (index > -1) {
                this.listeners[event].splice(index, 1);
            }
        }
    }
    
    /**
     * 销毁监听器，清理事件绑定
     */
    destroy() {
        // 移除触摸事件
        this.element.removeEventListener('touchstart', this.handleStart);
        this.element.removeEventListener('touchmove', this.handleMove);
        this.element.removeEventListener('touchend', this.handleEnd);
        
        // 移除鼠标事件
        this.element.removeEventListener('mousedown', this.handleStart);
        this.element.removeEventListener('mousemove', this.handleMove);
        this.element.removeEventListener('mouseup', this.handleEnd);
        this.element.removeEventListener('mouseleave', this.handleEnd);
        
        // 清空监听器
        Object.keys(this.listeners).forEach(key => {
            this.listeners[key] = [];
        });
    }
}














class ImageRotatorFixed {
    constructor(imageElement, options = {}) {
        this.image = imageElement;

        // 旋转配置
        this.rotateElement = options.rotateElement !== false;
        this.rotation = options.initialRotation || 0;
        this.startAngle = 0;
        this.isDragging = false;
        this.onRotate = options.onRotate || null;

        // 缩放配置
        this.scaleElement = options.scaleElement !== false;
        this.scale = options.initialScale || 1;
        this.minScale = options.minScale || 0.5;
        this.maxScale = options.maxScale || 3;
        this.onScale = options.onScale || null;

        // 触摸状态存储
        this.store = {
            scale: this.scale,
            originScale: 1,
            moveable: false,
            pageX: 0,
            pageY: 0,
            pageX2: 0,
            pageY2: 0
        };

        this.init();
    }

    init() {
        // 绑定事件处理器 - 旋转相关
        this.image.addEventListener('touchstart', this.handleStart.bind(this), { passive: false });
        this.image.addEventListener('touchmove', this.handleMove.bind(this), { passive: false });
        this.image.addEventListener('touchend', this.handleEnd.bind(this));

        // 绑定事件处理器 - 缩放相关
        this.image.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: false });
        document.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
        document.addEventListener('touchend', this.handleTouchEnd.bind(this));
        document.addEventListener('touchcancel', this.handleTouchEnd.bind(this));

        // 鼠标事件
        this.image.addEventListener('mousedown', this.handleStart.bind(this));
        document.addEventListener('mousemove', this.handleMove.bind(this));
        document.addEventListener('mouseup', this.handleEnd.bind(this));

        // 初始更新变换
        this.updateTransform();
    }

    // 处理触摸开始事件 - 缩放功能
    handleTouchStart(event) {
        const touches = event.touches;
        const events = touches[0];
        const events2 = touches[1];

        event.preventDefault();

        // 第一个触摸点的坐标
        this.store.pageX = events.pageX;
        this.store.pageY = events.pageY;
        this.store.moveable = true;

        if (events2) {
            this.store.pageX2 = events2.pageX;
            this.store.pageY2 = events2.pageY;
        }

        this.store.originScale = this.scale || 1;
    }

    // 处理触摸移动事件 - 缩放功能
    handleTouchMove(event) {
        if (!this.store.moveable) {
            return;
        }

        event.preventDefault();
        const touches = event.touches;
        const events = touches[0];
        const events2 = touches[1];

        // 双指移动 - 缩放处理
        if (events2) {
            // 第2个指头坐标在touchmove时获取
            if (!this.store.pageX2) {
                this.store.pageX2 = events2.pageX;
            }
            if (!this.store.pageY2) {
                this.store.pageY2 = events2.pageY;
            }

            // 计算两点之间的距离[1,2](@ref)
            const getDistance = (start, stop) => {
                return Math.hypot(stop.x - start.x, stop.y - start.y);
            };

            // 双指缩放比例计算[1,3](@ref)
            const zoom = getDistance({
                x: events.pageX,
                y: events.pageY
            }, {
                x: events2.pageX,
                y: events2.pageY
            }) / getDistance({
                x: this.store.pageX,
                y: this.store.pageY
            }, {
                x: this.store.pageX2,
                y: this.store.pageY2
            });

            // 应用在元素上的缩放比例[1](@ref)
            let newScale = this.store.originScale * zoom;

            // 缩放比例限制[2,4](@ref)
            if (newScale > this.maxScale) {
                newScale = this.maxScale;
            }
            if (newScale < this.minScale) {
                newScale = this.minScale;
            }

            // 更新缩放值
            this.scale = newScale;

            // 应用变换效果
            this.updateTransform();

            // 触发回调
            if (this.onScale) {
                this.onScale(this.scale);
            }
        }
    }

    // 处理触摸结束事件 - 缩放功能
    handleTouchEnd() {
        this.store.moveable = false;
        delete this.store.pageX2;
        delete this.store.pageY2;
    }

    // 计算两点之间的角度
    getAngle(centerX, centerY, x2, y2) {
        const dx = x2 - centerX;
        const dy = y2 - centerY;
        return Math.atan2(dy, dx) * 180 / Math.PI;
    }

    // 处理开始事件 - 旋转功能
    handleStart(event) {
        // 如果是双指操作，优先处理缩放
        if (event.touches && event.touches.length >= 2) {
            return;
        }

        event.preventDefault();
        this.isDragging = true;

        const rect = this.image.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;

        let clientX, clientY;

        if (event.type.includes('touch')) {
            clientX = event.touches[0].clientX;
            clientY = event.touches[0].clientY;
        } else {
            clientX = event.clientX;
            clientY = event.clientY;
        }

        this.startAngle = this.getAngle(centerX, centerY, clientX, clientY);
        this.previousAngle = this.startAngle;
    }

    // 处理移动事件 - 旋转功能
    handleMove(event) {
        // 如果是双指操作，优先处理缩放
        if (event.touches && event.touches.length >= 2) {
            return;
        }

        if (!this.isDragging) return;
        event.preventDefault();

        const rect = this.image.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;

        let clientX, clientY;

        if (event.type.includes('touch')) {
            clientX = event.touches[0].clientX;
            clientY = event.touches[0].clientY;
        } else {
            clientX = event.clientX;
            clientY = event.clientY;
        }

        const currentAngle = this.getAngle(centerX, centerY, clientX, clientY);

        // 计算角度差并处理跨周问题
        let angleDiff = currentAngle - this.previousAngle;

        // 处理360度边界情况（避免从359度到1度被识别为大角度变化）
        if (angleDiff > 180) {
            angleDiff -= 360;
        } else if (angleDiff < -180) {
            angleDiff += 360;
        }

        // 关键修复：减去角度差（而不是加上）来反转旋转方向
        this.rotation -= angleDiff;

        this.previousAngle = currentAngle;
        this.updateTransform();
    }

    // 处理结束事件
    handleEnd() {
        this.isDragging = false;
        this.previousAngle = null;
    }

    // 更新变换效果（同时处理旋转和缩放）
    updateTransform() {
        // 规范化角度到0-360范围
        this.rotation = this.rotation % 360;
        if (this.rotation < 0) this.rotation += 360;

        // 根据参数决定是否应用变换效果[8](@ref)
        let transformValue = '';

        if (this.scaleElement) {
            transformValue += `scale(${this.scale}) `;
        }

        if (this.rotateElement) {
            transformValue += `rotate(${this.rotation}deg)`;
        }

        if (transformValue) {
            this.image.style.transform = transformValue.trim();
        }

        // 如果有回调函数，则执行
        if (this.onRotate) {
            this.onRotate(this.rotation);
        }

        if (this.onScale) {
            this.onScale(this.scale);
        }
    }

    // 设置旋转角度
    setRotation(angle) {
        this.rotation = angle;
        this.updateTransform();
    }

    // 获取当前旋转角度
    getRotation() {
        return this.rotation;
    }

    // 设置缩放比例
    setScale(newScale) {
        // 缩放比例限制[2,4](@ref)
        if (newScale > this.maxScale) {
            newScale = this.maxScale;
        }
        if (newScale < this.minScale) {
            newScale = this.minScale;
        }

        this.scale = newScale;
        this.updateTransform();
    }

    // 获取当前缩放比例
    getScale() {
        return this.scale;
    }

    // 重置旋转和缩放
    reset() {
        this.setRotation(0);
        this.setScale(1);
    }

    // 销毁方法，清理事件监听
    destroy() {
        // 旋转相关事件
        this.image.removeEventListener('touchstart', this.handleStart);
        this.image.removeEventListener('touchmove', this.handleMove);
        this.image.removeEventListener('touchend', this.handleEnd);

        // 缩放相关事件
        this.image.removeEventListener('touchstart', this.handleTouchStart);
        document.removeEventListener('touchmove', this.handleTouchMove);
        document.removeEventListener('touchend', this.handleTouchEnd);
        document.removeEventListener('touchcancel', this.handleTouchEnd);

        // 鼠标事件
        this.image.removeEventListener('mousedown', this.handleStart);
        document.removeEventListener('mousemove', this.handleMove);
        document.removeEventListener('mouseup', this.handleEnd);
    }
}




/**
 * 计算两个日期时间对象之间的差异，并返回友好的中文描述（如"X天后"或"X天前"）
 * @param {Object} dateObj1 - 第一个日期时间对象，包含年(y)、月(m)、日(d)、时(h)、分(i)属性
 * @param {Object} dateObj2 - 第二个日期时间对象，格式同dateObj1
 * @returns {string} 描述时间差异的字符串，例如 "25天后" 或 "5天前"
 */
function getDateDifference(dateObj1, dateObj2) {
    // 1. 将JSON参数转换为Date对象 [1,3,4](@ref)
    // 注意：JavaScript中月份是从0开始计数的（0代表一月），所以需要将月份减1 [3,4](@ref)
    const date1 = new Date(dateObj1.y, dateObj1.m - 1, dateObj1.d, dateObj1.h, dateObj1.i);
    const date2 = new Date(dateObj2.y, dateObj2.m - 1, dateObj2.d, dateObj2.h, dateObj2.i);

    // 2. 计算两个日期的时间戳差值（毫秒）并转换为天数 [1,2,4](@ref)
    const timeDiff = date2.getTime() - date1.getTime(); // 获取毫秒差 [2,6](@ref)
    const daysDiff = timeDiff / (1000 * 60 * 60 * 24); // 将毫秒转换为天数 [1,2,4](@ref)

    // 3. 对天数进行取整，并确定返回的字符串
    const roundedDaysDiff = Math.round(daysDiff); // 对天数进行四舍五入取整

    if (roundedDaysDiff > 0) {
        return `${roundedDaysDiff}天后`;
    } else if (roundedDaysDiff < 0) {
        return `${Math.abs(roundedDaysDiff)}天前`; // 使用绝对值确保输出正数
    } else {
        return "今天"; // 或者可以返回 "同一天"
    }
}
// console.log(typeof yueLiCalc)