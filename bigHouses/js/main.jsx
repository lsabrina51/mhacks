import React, { StrictMode, useState, useEffect } from "react";
import InfiniteScroll from "react-infinite-scroll-component";
import { createRoot } from "react-dom/client";
import Post from "./post";

// Create a root
const root = createRoot(document.getElementById("reactEntry"));

// Get all posts we need
function PostList({ url }) {
  /* Display image and post owner of a single post */

  const [posts, setPosts] = useState([]);
  const [nextUrl, setNextUrl] = useState("");

  useEffect(() => {
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStaleRequest = false;

    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          setPosts(data.results);
          setNextUrl(data.next);
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url]); // Updates useEffect based on URL

  // useEffect(() => {})
  const fetchMoreData = () => {
    // a fake async api call like which sends
    // 20 more records in 1.5 secs
    // setTimeout(() => {
    //   this.setState({
    //     items: this.state.items.concat(Array.from({ length: 20 }))
    //   });
    // }, 1500);
    let ignoreStaleRequest = false;

    // Call REST API to get the post's information
    fetch(nextUrl, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          // appending the new posts (data.results) to orig posts
          setPosts([...posts, ...data.results]);
          setNextUrl(data.next); // update w new nextUrl
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  };

  // Render each post
  return (
    <StrictMode>
      <div>
        <InfiniteScroll
          dataLength={posts.length}
          next={fetchMoreData}
          hasMore={nextUrl !== ""}
          loader={<h4>Loading...</h4>}
        >
          {posts.map((post) => (
            <Post key={post.housing_id} url={post.url} />
          ))}
          {/* {nextUrl && <a href={nextUrl}>Next Page</a>} */}
        </InfiniteScroll>
      </div>
    </StrictMode>
  );
}

// Insert the post component into the DOM.  Only call root.render() once.
root.render(
  <StrictMode>
    <PostList url="/api/v1/posts/" />
  </StrictMode>,
);
