import React from 'react';

const Logo = () => {
  console.log('Rendering Logo component');

  return (
    <div className="logo">
      <a href="/">
        <img src="/path-to-logo.png" alt="Company Logo" />
      </a>
    </div>
  );
};

export default Logo;