/**
 * Modal Component JavaScript
 *
 * Provides functionality for showing, hiding, and interacting with modals
 */
document.addEventListener('DOMContentLoaded', function() {
  // Modal class
  class Modal {
    constructor(element) {
      this.element = element;
      this.id = element.id;
      this.closeButtons = element.querySelectorAll('[data-dismiss="modal"]');
      this.confirmButton = element.querySelector('.modal-confirm');
      this.backdrop = element.querySelector('.modal-backdrop');
      this.dialog = element.querySelector('.modal-dialog');
      this.isVisible = false;
      this.onConfirm = null;
      this.onDismiss = null;

      this.init();
    }

    init() {
      // Close button click
      this.closeButtons.forEach(button => {
        button.addEventListener('click', () => this.hide());
      });

      // Confirm button click
      if (this.confirmButton) {
        this.confirmButton.addEventListener('click', () => {
          if (typeof this.onConfirm === 'function') {
            this.onConfirm();
          }
          this.hide();
        });
      }

      // Backdrop click
      if (this.backdrop) {
        this.backdrop.addEventListener('click', () => this.hide());
      }

      // Prevent dialog click from closing modal
      if (this.dialog) {
        this.dialog.addEventListener('click', (e) => e.stopPropagation());
      }

      // Escape key press
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.isVisible) {
          this.hide();
        }
      });
    }

    show() {
      this.isVisible = true;
      this.element.classList.add('show');
      document.body.style.overflow = 'hidden';

      // Focus first focusable element
      setTimeout(() => {
        const focusable = this.element.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusable.length) {
          focusable[0].focus();
        }
      }, 300);
    }

    hide() {
      this.isVisible = false;
      this.element.classList.remove('show');
      document.body.style.overflow = '';

      if (typeof this.onDismiss === 'function') {
        this.onDismiss();
      }
    }

    setContent(content) {
      const body = this.element.querySelector('.modal-body');
      if (body) {
        body.innerHTML = content;
      }
    }

    setTitle(title) {
      const titleElement = this.element.querySelector('.modal-title');
      if (titleElement) {
        titleElement.textContent = title;
      }
    }

    setOnConfirm(callback) {
      this.onConfirm = callback;
    }

    setOnDismiss(callback) {
      this.onDismiss = callback;
    }
  }

  // Initialize all modals
  const modalElements = document.querySelectorAll('.modal');
  const modals = {};

  modalElements.forEach(modalElement => {
    const modal = new Modal(modalElement);
    modals[modal.id] = modal;
  });

  // Make modals available globally
  window.Modals = modals;

  // Add open modal function for buttons with data-toggle="modal"
  document.querySelectorAll('[data-toggle="modal"]').forEach(button => {
    const targetId = button.getAttribute('data-target');
    if (targetId && modals[targetId.substring(1)]) {
      button.addEventListener('click', () => {
        modals[targetId.substring(1)].show();
      });
    }
  });
});