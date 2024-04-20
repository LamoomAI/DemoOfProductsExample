import React from 'react';
import { Link } from 'react-router-dom';

const NavigationLink = ({ to, label }) => {
  return (
    <Link to={to} className="navigation-link">
      {label}
    </Link>
  );
};

export default NavigationLink;