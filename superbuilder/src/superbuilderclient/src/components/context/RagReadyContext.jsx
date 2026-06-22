import { createContext, useState } from 'react';

const RagReadyContext = createContext({
 ready: false,
 setReady: () => {},
});

const RagReadyProvider = ({ children }) => {
 const [ready, setReady] = useState();

 return (
   <RagReadyContext.Provider value={{ ready, setReady }}>
     {children}
   </RagReadyContext.Provider>
 );
};

export { RagReadyContext, RagReadyProvider };