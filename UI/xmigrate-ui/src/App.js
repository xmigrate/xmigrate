import React from "react";
import "./App.css";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import Home from "./pages/Home/Home";
import SignIn from "./pages/SignIn/SignIn";
import Project from "./pages/Project/Project";
import SignUp from "./pages/SignUp/SignUp";
import ErrorPage from "./pages/Error/ErrorPage";
import { ProtectedRoute } from "./services/Protected.route";

function App() {
  return (
    <div className="App h-100">
      <Router>
        <Switch>
          <Route exact path="/" component={SignIn} />
          <Route exact path="/signup" component={SignUp} />
          <ProtectedRoute path="/home" component={Home} />
          <ProtectedRoute path="/Project" component={Project} />
          <Route path="/404" component={()=><ErrorPage err={"404"} />} />
          <Route path="/401" component={()=><ErrorPage err={"401"} />} />
          <Route path="/500" component={()=><ErrorPage err={"500"} />} />
          <Route path="/400" component={()=><ErrorPage err={"400"} />} />
          <Route
            path="/error"
            component={() => {
              return (
                <div className="d-flex justify-content-center align-items-center h-100">
                  <h4>Sry For the Error!! Will fix it soon</h4>
                </div>
              );
            }}
          />
        </Switch>
      </Router>
    </div>
  );
}

export default App;
