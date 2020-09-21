import React from "react";
import "./App.css";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
// import BluePrint from './pages/BluePrint/BluePrint';
// import CreateWorkspace from './pages/CreateWorkspace/CreateWorkspace';
// import Dashboard from './pages/Dashboard/Dashboard';
import Home from "./pages/Home/Home";
import SignIn from "./pages/SignIn/SignIn";
import Project from "./pages/Project/Project";
import SignUp from "./pages/SignUp/SignUp";
import {ProtectedRoute} from './services/Protected.route';

function App() {
  return (
    <div className="App h-100">
      <Router>
        <Switch>
        <Route exact path="/" component={SignIn} />
          <Route exact path="/signup" component={SignUp} />
          <ProtectedRoute  path="/home" component={Home} />
          <ProtectedRoute  path="/Project" component={Project} />
          <Route path="*" component={()=>"404 not found"}/>
        </Switch>
      </Router>
    </div>
  );
}

export default App;
