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
import Landpage from './pages/Landpage/Landpage'
import { TitleComponent } from './components/TitleComponent/TitleComponent';

function App() {
  return (
   
    <div className="App h-100">
 <TitleComponent />
      <Router>


        <Switch>
          <Route path="/" component={Home} />
         
        </Switch>

      </Router>


    </div>
  );
}

export default App;
