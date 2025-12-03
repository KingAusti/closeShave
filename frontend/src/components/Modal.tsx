import React from 'react'
import './Modal.css'

interface ModalProps {
    isOpen: boolean
    onClose: () => void
    title: string
    children: React.ReactNode
    type?: 'info' | 'error' | 'warning'
}

export default function Modal({ isOpen, onClose, title, children, type = 'info' }: ModalProps) {
    if (!isOpen) return null

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className={`modal-content modal-${type}`} onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <h2 className="modal-title">{title}</h2>
                    <button className="modal-close" onClick={onClose}>
                        &times;
                    </button>
                </div>
                <div className="modal-body">{children}</div>
                <div className="modal-footer">
                    <button className="neon-button" onClick={onClose}>
                        Close
                    </button>
                </div>
            </div>
        </div>
    )
}
