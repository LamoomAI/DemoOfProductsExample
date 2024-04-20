import React from 'react';

const Button = ({ onClick, children, disabled }) => {
  return (
    <button onClick={onClick} disabled={disabled} className="button">
      {children}
    </button>
  );
};

export default Button;