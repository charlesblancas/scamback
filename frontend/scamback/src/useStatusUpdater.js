import React, { useState, useEffect, useRef } from "react";


export const useStatusUpdater = () => {
    const [status, setStatus] = useState(null);
  
    useEffect(() => {
      const fetchStatus = async () => {
        try {
          const response = await fetch("http://localhost:5785/status");
          if (!response.ok) {
            throw new Error("Failed to fetch status");
          }
          console.log(response)
          const data = await response.json();
          setStatus(data["status"]);
        } catch (error) {
          console.error("Error fetching status:", error);
          setStatus("Error fetching status");
        }
      };
  
      const intervalId = setInterval(fetchStatus, 1000);
  
      return () => clearInterval(intervalId);
    }, []);
  
    return status;
  };