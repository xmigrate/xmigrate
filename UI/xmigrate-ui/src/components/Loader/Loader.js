import React from 'react'
import "./LoaderComponent.scss";

 export default function Loader() {
    return (
        <div className="d-flex justify-content-center align-items-center h-100">
<div className="spinner">
  <div className="double-bounce1"></div>
  <div className="double-bounce2"></div>
</div>
</div>
    );
  }

