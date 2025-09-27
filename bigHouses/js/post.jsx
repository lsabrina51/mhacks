import React, { useState, useEffect } from "react";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";

dayjs.extend(relativeTime);
dayjs.extend(utc);

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Post({ url }) {
  /* Display image and post owner of a single post */
  const [imgUrl, setImgUrl] = useState("");
  const [headerData, setHeaderData] = useState(null);
  const [numLikes, setNumLikes] = useState(0);
  const [logLiked, setLogLiked] = useState(false);
  const [likeUrl, setLikeUrl] = useState("");
  // const [owner, setOwner] = useState(""); - in post header
  const [comments, setComments] = useState([]);

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
          setImgUrl(data.imgUrl);
          setHeaderData(data);
          setNumLikes(data.likes.numLikes);
          setLogLiked(data.likes.lognameLikesThis);
          setLikeUrl(data.likes.url);
          setComments(data.comments); // data.comments[0].text
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url]);

  // for DOUBLE CLICK
  const onlyLike = () => {
    if (!logLiked) {
      const addUrl = `/api/v1/likes/?postid=${headerData.postid}`;
      fetch(addUrl, {
        method: "POST",
        credentials: "same-origin",
      })
        // once add like request is sent, need to update state
        // state makes updates to UI immediately, assuming fetch worked
        .then((response) => response.json())
        .then((data) => {
          // console.log("data.likeid = " , data.likeid)
          setLikeUrl(data.url); // Update likeUrl with new ID
        })
        .then(() => {
          setLogLiked(true);
          setNumLikes(numLikes + 1);
        })
        .catch((error) => console.log("Error liking post:", error));
    }
  };

  const handleLikes = () => {
    // if prev liked, then UNLIKE:
    if (logLiked) {
      fetch(likeUrl, {
        method: "DELETE",
        credentials: "same-origin",
      })
        // once delete request is sent, need to update state
        // state makes updates to UI immediately, assuming fetch worked
        .then(() => {
          setLogLiked(false);
          setNumLikes((PrevNumLikes) => PrevNumLikes - 1);
        })
        .catch((error) => console.log("Error unliking post:", error));
    }

    // if prev unliked, then LIKE:
    else {
      const addUrl = `/api/v1/likes/?postid=${headerData.postid}`;
      fetch(addUrl, {
        method: "POST",
        credentials: "same-origin",
      })
        // once add like request is sent, need to update state
        // state makes updates to UI immediately, assuming fetch worked
        .then((response) => response.json())
        .then((data) => {
          // console.log("data.likeid = " , data.likeid)
          setLikeUrl(data.url); // Update likeUrl with new ID
        })
        .then(() => {
          setLogLiked(true);
          setNumLikes((PrevNumLikes) => PrevNumLikes + 1);
        })
        .catch((error) => console.log("Error liking post:", error));
    }
  };

  const deleteComments = (commentid, commentUrl) => {
    fetch(commentUrl, {
      method: "DELETE",
      credentials: "same-origin",
    })
      // once delete request is sent, need to update state
      // state makes updates to UI immediately, assuming fetch worked
      // remove old comment from data.comments and set it to new list
      .then(() => {
        // setComments(prevComments => prevComments + newComment;
        setComments((prevComments) =>
          prevComments.filter((comment) => comment.commentid !== commentid),
        );
      })
      .catch((error) => console.log("Error deleting a comment:", error));
  };

  const addComments = (inputText) => {
    const urlD = `/api/v1/comments/?postid=${headerData.postid}`;
    // body: JSON.stringify({ text: document.getElementById("comment").value })
    // console.log(`${url}`)
    fetch(urlD, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: inputText }),
      credentials: "same-origin",
    })
      // once delete request is sent, need to update state
      // state makes updates to UI immediately, assuming fetch worked
      .then((response) => response.json())
      .then((data) => {
        // console.log("DATA: ", data)
        // console.log("DATA TEXT: ", data.text)
        // console.log("inputText: ", inputText)

        // console.log([...comments, ...[data]])
        setComments([...comments, ...[data]]);
      })
      .catch((error) => console.log("Error commenting on post:", error));
    // }
  };

  if (headerData === null) {
    return <div id="reactEntry">Loading ...</div>;
  }
  // Render post image and post owner
  // if null is post return loading
  return (
    <div className="post">
      <PostHeader info={headerData} />

      <img
        src={imgUrl}
        alt="post_image"
        onDoubleClick={onlyLike}
        style={{ pointerEvents: "all" }}
      />

      <Likes
        numLikes={numLikes}
        logLiked={logLiked}
        handleLikes={handleLikes}
      />

      <Comments
        allComments={comments}
        addComment={addComments}
        deleteComment={deleteComments}
      />
    </div>
  );
}

// POST HEADER WORKS NOW :)
export function PostHeader({ info }) {
  // Convert UTC to local time
  const created = dayjs(info.created).utc(true).local();
  const relative = created.fromNow();

  return (
    <div className="post-header">
      <a href={info.ownerShowUrl}> {info.owner} </a>
      <a href={info.ownerShowUrl}>
        <img src={info.ownerImgUrl} alt="profile pic" />
      </a>
      {/* Human readable timestamp */}
      <a href={info.postShowUrl}> {relative} </a>
    </div>
  );
}

/*
Pro-tip: If you decide to create a Likes or Comments component, use the Lifting State Up technique.
The parent Post component stores the state (number of likes) and a state setter function.
The child Likes component displays the number of likes, which is passed as props by the parent Post component.
The child Likes component uses a function reference passed as props by the parent Post component when the Like button is pressed.
*/

export function Likes({ numLikes, logLiked, handleLikes }) {
  // QUESTION - slow server fails? WHY ?
  // ensure button only loads once data is rendered:
  if (numLikes === undefined || logLiked === undefined) {
    return null;
  }

  let buttonLine = "";
  if (logLiked) {
    buttonLine = "Unlike";
  } else {
    buttonLine = "Like";
  }

  let likeLine = "";
  if (numLikes === 1) {
    likeLine = " like";
  } else {
    likeLine = " likes";
  }

  return (
    <div>
      <p>
        {" "}
        {numLikes} {likeLine}{" "}
      </p>
      {/* Event handler: onClick calls handleLikes func */}
      <button
        type="button"
        data-testid="like-unlike-button"
        onClick={handleLikes}
      >
        {buttonLine}
      </button>
    </div>
  );
}

export function Comments({ allComments, deleteComment, addComment }) {
  const [inputText, setInputText] = useState("");

  function handleKeyDown(event) {
    if (event.key === "Enter") {
      // console.log("COMMENT SUBMISSION: ", inputText);
      event.preventDefault();
      addComment(inputText);
      setInputText("");
    }
  }

  function addInput(event) {
    setInputText(event.target.value);
  }

  return (
    <div>
      {allComments.map((comment) => (
        <div key={comment.commentid}>
          {/* display comments */}
          <p>
            <a href={comment.ownerShowUrl}>
              {" "}
              <strong>{comment.owner}</strong>
            </a>
            <span data-testid="comment-text"> {comment.text}</span>
          </p>
          {/* display Delete comment button if logname owns, pass commid to delete */}
          {comment.lognameOwnsThis && (
            // deleteComment needs to be sent as a reference, so use () =>'
            <button
              type="button"
              data-testid="delete-comment-button"
              onClick={() => deleteComment(comment.commentid, comment.url)}
            >
              Delete
            </button>
          )}
        </div>
      ))}
      {/* Add comment form */}
      {/* onKeyDown={addComment} */}
      <form data-testid="comment-form">
        {/* update text in input box as they type */}
        <input
          type="text"
          value={inputText}
          onChange={addInput}
          onKeyDown={handleKeyDown}
        />
        {/* <input type="submit" value="add"/> */}
      </form>
    </div>
  );
}
