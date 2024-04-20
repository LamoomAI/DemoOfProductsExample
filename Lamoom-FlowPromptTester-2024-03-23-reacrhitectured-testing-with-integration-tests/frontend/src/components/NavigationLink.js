import React from 'react';

const NavigationLink = ({ href, label }) => {
  console.log(`Rendering NavigationLink component for ${label}`);

  return (
    <a href={href} className="text-blue-500 hover:text-blue-700 px-4 py-2 transition-colors duration-200">
      {label}
    </a>
  );
};

export default NavigationLink;