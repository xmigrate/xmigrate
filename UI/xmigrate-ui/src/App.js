import React from 'react';
import './App.css';
import {
  BrowserRouter as Router,
  Switch,
  Route,
} from "react-router-dom";
// import BluePrint from './pages/BluePrint/BluePrint';
// import CreateWorkspace from './pages/CreateWorkspace/CreateWorkspace';
// import Dashboard from './pages/Dashboard/Dashboard';
import Home from './pages/Home/Home';

function App() {
  return (
    <div className="App h-100">

      <Router>


        <Switch>
          <Route path="/" component={Home} />
         
        </Switch>

      </Router>


    </div>
  );
}

export default App;
