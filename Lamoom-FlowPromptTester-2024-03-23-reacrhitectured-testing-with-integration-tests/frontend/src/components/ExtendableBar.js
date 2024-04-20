import React from 'react';
import PropTypes from 'prop-types';

const ExtendableBar = ({ children }) => {
  // Log to console when the component is rendered
  console.log('ExtendableBar is rendered with children:', children);

  return (
    <div className="bg-gray-100 p-4 rounded-lg shadow-md">
      {children}
    </div>
  );
};

ExtendableBar.propTypes = {
  children: PropTypes.node.isRequired,
};

export default ExtendableBar;