import React, { useEffect, useRef } from 'react'
import './Modal.css'

interface ModalProps {
    isOpen: boolean
    onClose: () => void
    title: string
    children: React.ReactNode
    type?: 'info' | 'error' | 'warning'
    onRetry?: () => void
}

export default function Modal({ isOpen, onClose, title, children, type = 'info', onRetry }: ModalProps) {
    const modalRef = useRef<HTMLDivElement>(null)
    const closeButtonRef = useRef<HTMLButtonElement>(null)
    const previousActiveElement = useRef<HTMLElement | null>(null)

    useEffect(() => {
        if (isOpen) {
            // Store the previously focused element
            previousActiveElement.current = document.activeElement as HTMLElement

            // Focus the close button when modal opens
            setTimeout(() => {
                closeButtonRef.current?.focus()
            }, 0)

            // Handle Escape key
            const handleEscape = (e: KeyboardEvent) => {
                if (e.key === 'Escape') {
                    onClose()
                }
            }

            document.addEventListener('keydown', handleEscape)

            // Trap focus within modal
            const handleTab = (e: KeyboardEvent) => {
                if (e.key !== 'Tab') return

                const modal = modalRef.current
                if (!modal) return

                const focusableElements = modal.querySelectorAll<HTMLElement>(
                    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                )
                const firstElement = focusableElements[0]
                const lastElement = focusableElements[focusableElements.length - 1]

                if (e.shiftKey) {
                    // Shift + Tab
                    if (document.activeElement === firstElement) {
                        e.preventDefault()
                        lastElement?.focus()
                    }
                } else {
                    // Tab
                    if (document.activeElement === lastElement) {
                        e.preventDefault()
                        firstElement?.focus()
                    }
                }
            }

            document.addEventListener('keydown', handleTab)

            return () => {
                document.removeEventListener('keydown', handleEscape)
                document.removeEventListener('keydown', handleTab)
                // Restore focus to previous element
                previousActiveElement.current?.focus()
            }
        }
    }, [isOpen, onClose])

    if (!isOpen) return null

    return (
        <div
            className="modal-overlay"
            onClick={onClose}
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-title"
        >
            <div
                ref={modalRef}
                className={`modal-content modal-${type}`}
                onClick={e => e.stopPropagation()}
            >
                <div className="modal-header">
                    <h2 id="modal-title" className="modal-title">{title}</h2>
                    <button
                        ref={closeButtonRef}
                        className="modal-close"
                        onClick={onClose}
                        aria-label="Close dialog"
                    >
                        &times;
                    </button>
                </div>
                <div className="modal-body">{children}</div>
                <div className="modal-footer">
                    {onRetry && (
                        <button className="neon-button" onClick={onRetry} aria-label="Retry search">
                            Retry
                        </button>
                    )}
                    <button className="neon-button" onClick={onClose} aria-label="Close dialog">
                        Close
                    </button>
                </div>
            </div>
        </div>
    )
}
