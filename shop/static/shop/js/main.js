/**
 * Sweet Slice Artisanal Bakery - Interactive UI & Razorpay Demo Engine
 */

document.addEventListener("DOMContentLoaded", function () {
    // 1. Sticky Header elevation on scroll
    const header = document.querySelector(".boutique-nav") || document.querySelector(".site-header");
    window.addEventListener("scroll", () => {
        if (window.scrollY > 20) {
            header?.classList.add("scrolled");
        } else {
            header?.classList.remove("scrolled");
        }
    });

    // 2. Mobile Drawer & Backdrop Navigation
    const mobileToggle = document.querySelector("#mobileMenuTrigger");
    const mobileDrawer = document.querySelector("#mobileDrawer");
    const mobileBackdrop = document.querySelector("#mobileDrawerBackdrop");
    const mobileDrawerClose = document.querySelector("#mobileDrawerClose");

    function openMobileDrawer() {
        if (!mobileDrawer) return;
        mobileDrawer.classList.add("is-open");
        mobileDrawer.setAttribute("aria-hidden", "false");
        mobileBackdrop?.classList.add("is-active");
        mobileToggle?.setAttribute("aria-expanded", "true");
        document.body.classList.add("drawer-open");
    }

    function closeMobileDrawer() {
        if (!mobileDrawer) return;
        mobileDrawer.classList.remove("is-open");
        mobileDrawer.setAttribute("aria-hidden", "true");
        mobileBackdrop?.classList.remove("is-active");
        mobileToggle?.setAttribute("aria-expanded", "false");
        document.body.classList.remove("drawer-open");
    }

    if (mobileToggle) {
        mobileToggle.addEventListener("click", () => {
            const isOpen = mobileDrawer?.classList.contains("is-open");
            if (isOpen) {
                closeMobileDrawer();
            } else {
                openMobileDrawer();
            }
        });
    }

    if (mobileDrawerClose) {
        mobileDrawerClose.addEventListener("click", closeMobileDrawer);
    }

    if (mobileBackdrop) {
        mobileBackdrop.addEventListener("click", closeMobileDrawer);
    }

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && mobileDrawer?.classList.contains("is-open")) {
            closeMobileDrawer();
        }
    });

    // Close drawer when a link inside it is clicked
    document.querySelectorAll(".mobile-nav-link").forEach((link) => {
        link.addEventListener("click", () => {
            closeMobileDrawer();
        });
    });

    // 3. Weight Selector dynamic price adjustments on cards & detail
    document.querySelectorAll(".weight-pill-btn").forEach((btn) => {
        btn.addEventListener("click", function () {
            const container = this.closest(".cake-card") || this.closest(".cake-detail-card");
            if (!container) return;

            container.querySelectorAll(".weight-pill-btn").forEach((b) => b.classList.remove("active"));
            this.classList.add("active");

            const selectedWeight = this.dataset.weight;
            const basePrice = parseFloat(container.dataset.basePrice || 0);
            let multiplier = 1.0;

            if (selectedWeight.includes("0.5")) multiplier = 0.6;
            else if (selectedWeight.includes("1.5")) multiplier = 1.5;
            else if (selectedWeight.includes("2")) multiplier = 1.9;

            const computedPrice = Math.round(basePrice * multiplier);
            const priceDisplay = container.querySelector(".dynamic-price");
            if (priceDisplay) {
                priceDisplay.textContent = "₹" + computedPrice;
            }

            const hiddenWeightInput = container.querySelector("input[name='weight']");
            if (hiddenWeightInput) {
                hiddenWeightInput.value = selectedWeight;
            }
        });
    });

    // 4. AJAX Add to Cart for instant smooth feel
    document.querySelectorAll(".ajax-add-cart-form").forEach((form) => {
        form.addEventListener("submit", function (e) {
            e.preventDefault();
            const submitBtn = this.querySelector("button[type='submit']");
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = "<span>Adding...</span>";

            const formData = new FormData(this);
            formData.append("ajax", "1");

            fetch(this.action, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: formData,
            })
                .then((res) => res.json())
                .then((data) => {
                    if (data.require_login) {
                        showToast(data.message || "Please sign in to order this cake!", "info");
                        setTimeout(() => {
                            window.location.href = data.redirect_url || "/login/";
                        }, 600);
                        return;
                    }

                    submitBtn.disabled = false;
                    submitBtn.innerHTML = "<span>✓ Added!</span>";
                    setTimeout(() => {
                        submitBtn.innerHTML = originalText;
                    }, 1800);

                    // Update header cart count
                    if (data.cart_count !== undefined) {
                        document.querySelectorAll(".cart-count-bubble, .cart-badge").forEach((b) => {
                            b.textContent = data.cart_count;
                        });
                    }

                    showToast(data.message || "Item added to cart!", "success");
                })
                .catch(() => {
                    // Fallback to regular form submission if fetch fails
                    form.submit();
                });
        });
    });

    // 5. Quantity Steppers in Cart
    document.querySelectorAll(".ajax-qty-btn").forEach((btn) => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            const cakeId = this.dataset.cakeId;
            const action = this.dataset.action;
            const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value;

            const formData = new FormData();
            formData.append("action", action);
            formData.append("ajax", "1");
            if (csrfToken) formData.append("csrfmiddlewaretoken", csrfToken);

            fetch(`/cart/update/${cakeId}/`, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: formData,
            })
                .then((res) => res.json())
                .then((data) => {
                    if (data.success) {
                        window.location.reload();
                    }
                })
                .catch(() => window.location.reload());
        });
    });
});

/**
 * Toast Notification System
 */
function showToast(message, type = "info") {
    let container = document.querySelector(".toast-container");
    if (!container) {
        container = document.createElement("div");
        container.className = "toast-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    const icon = type === "success" ? "🍰" : type === "error" ? "⚠️" : "✨";
    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(100%)";
        toast.style.transition = "all 0.3s ease";
        setTimeout(() => toast.remove(), 350);
    }, 3500);
}

/**
 * Razorpay Demo Payment Modal Engine
 */
function openRazorpayDemoModal(options) {
    const backdrop = document.getElementById("razorpayModalBackdrop");
    if (!backdrop) return;

    // Prefill modal values
    const amountDisplay = document.getElementById("rzpModalAmount");
    if (amountDisplay) amountDisplay.textContent = "₹" + options.amount;

    backdrop.classList.add("active");
    window.currentRzpOptions = options;
}

function closeRazorpayDemoModal() {
    const backdrop = document.getElementById("razorpayModalBackdrop");
    if (backdrop) backdrop.classList.remove("active");
}

function switchRzpTab(tabName) {
    document.querySelectorAll(".rzp-tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".rzp-tab-content").forEach((c) => (c.style.display = "none"));

    const activeBtn = document.querySelector(`[data-rzp-tab='${tabName}']`);
    const activeContent = document.getElementById(`rzpTab_${tabName}`);
    if (activeBtn) activeBtn.classList.add("active");
    if (activeContent) activeContent.style.display = "block";
}

function completeDemoPayment(methodName) {
    const btn = document.getElementById("btnConfirmRzpPay");
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span class="spinner"></span> Processing ₹${window.currentRzpOptions?.amount || ''}...`;
    }

    // Simulate bank authentication & webhook verification delay
    setTimeout(() => {
        const randId = "pay_live_" + Math.random().toString(36).substring(2, 12).toUpperCase();

        // Populate hidden inputs in checkout form and submit
        const form = document.getElementById("checkoutOrderForm");
        if (form) {
            document.getElementById("hiddenRazorpayPaymentId").value = randId;
            document.getElementById("hiddenPaymentMethod").value = "Razorpay (" + methodName + ")";
            form.submit();
        } else {
            window.location.href = `/order/success/demo/?pay_id=${randId}`;
        }
    }, 1200);
}

/**
 * Admin Panel Modal Handlers (Add, Edit, Delete)
 */
function openAddCakeModal() {
    const modal = document.getElementById("adminAddCakeModal");
    if (modal) modal.classList.add("active");
}

function closeAddCakeModal() {
    const modal = document.getElementById("adminAddCakeModal");
    if (modal) modal.classList.remove("active");
}

function openEditCakeModal(cakeId) {
    fetch(`/dashboard/cake/edit/${cakeId}/`)
        .then((res) => res.json())
        .then((data) => {
            const form = document.getElementById("editCakeForm");
            if (!form) return;

            form.action = `/dashboard/cake/edit/${cakeId}/`;
            form.querySelector("[name='name']").value = data.name;
            form.querySelector("[name='category']").value = data.category;
            form.querySelector("[name='price']").value = data.price;
            form.querySelector("[name='original_price']").value = data.original_price || "";
            form.querySelector("[name='image_url']").value = data.image_url;
            form.querySelector("[name='badge']").value = data.badge || "";
            form.querySelector("[name='weight_options']").value = data.weight_options || "";
            form.querySelector("[name='description']").value = data.description || "";
            form.querySelector("[name='is_eggless']").checked = !!data.is_eggless;
            form.querySelector("[name='available']").checked = !!data.available;

            const modal = document.getElementById("adminEditCakeModal");
            if (modal) modal.classList.add("active");
        })
        .catch((err) => {
            showToast("Failed to load cake details", "error");
        });
}

function closeEditCakeModal() {
    const modal = document.getElementById("adminEditCakeModal");
    if (modal) modal.classList.remove("active");
}

function confirmDeleteCake(cakeId, cakeName) {
    if (confirm(`Are you sure you want to permanently delete '${cakeName}' from the menu?`)) {
        window.location.href = `/dashboard/cake/delete/${cakeId}/`;
    }
}
